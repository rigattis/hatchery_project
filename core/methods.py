"""Cross-app helper methods for common operations.

- Training/certification summary for the currently logged-in user
- Machine availability checks

These methods use direct model queries instead of calling app services.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Union

from django.contrib.auth.models import AnonymousUser

from pct.models import Person, Certification, TrainingRecord
from cmr.models import Machine, Reservation


def _get_person_for_user(user) -> Optional[Dict[str, Any]]:
    """Map a Django user to an existing Person row by email.

    Assumes the user is authenticated (not anonymous) and a Person record already exists.

    Args:
        user: Django User instance (from request.user or similar) - must be authenticated

    Returns:
        Dict with 'name' (full name) and 'type' (role), or None if no email or no matching Person exists.

    Example Input:
        user = request.user  # Django User with email='bob@example.com'

    Example Output (person exists - Team Member):
        {
            'name': 'Bob Smith',
            'type': 'Team Member'
        }

    Example Output (person exists - Team Lead):
        {
            'name': 'Alice Johnson',
            'type': 'Team Lead'
        }

    Example Output (person exists - Staff):
        {
            'name': 'Carol Williams',
            'type': 'Staff'
        }

    Example Output (person doesn't exist):
        None

    Returns None if the user has no email or no Person record exists for that email.
    """
    email = getattr(user, "email", None)
    if not email:
        return None
    # Direct model query - only retrieve, never create
    try:
        person = Person.objects.get(email=email)
        # Determine type: if Team Member and is_team_lead, type is 'Team Lead'
        person_type = 'Team Lead' if (person.role == 'Team Member' and person.is_team_lead) else person.role
        return {
            'name': f"{person.first_name} {person.last_name}".strip(),
            'type': person_type
        }
    except Person.DoesNotExist:
        return None


def get_user_training_summary(user) -> Optional[Dict[str, Any]]:
    """Return a structured summary of certifications and training for the logged-in user.

    Args:
        user: Django User instance (from request.user or similar)

    Returns:
        Dict with person info, certifications, and training records, or None if anonymous/no email.

    Example Input:
        user = request.user  # Django User with email='alice@example.com'

    Example Output:
        {
            'person_id': 42,
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'role': 'Team Member',
            'is_team_lead': True,
            'certifications': [
                {
                    'name': 'Laser Cutter Safety',
                    'issued_at': date(2024, 3, 15),
                    'expires_at': date(2025, 3, 15)
                },
                {
                    'name': '3D Printer Operator',
                    'issued_at': date(2024, 1, 10),
                    'expires_at': None
                }
            ],
            'training': [
                {
                    'course_name': 'Advanced Woodworking',
                    'completed_at': datetime(2024, 9, 20, 14, 30, tzinfo=UTC),
                    'training_course': {
                        'id': 5,
                        'category': 'Woodworking',
                        'level': 2
                    }
                },
                {
                    'course_name': 'Basic Shop Safety',
                    'completed_at': datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
                    'training_course': None  # Free-text training without catalog entry
                }
            ]
        }

    Returns None if the user is anonymous or has no email.
    """
    person_info = _get_person_for_user(user)
    if not person_info:
        return None

    # Retrieve the actual Person instance for querying certifications and training
    email = getattr(user, "email", None)
    try:
        person = Person.objects.get(email=email)
    except Person.DoesNotExist:
        return None

    certs = [
        {
            "name": c.name,
            "issued_at": c.issued_at,
            "expires_at": c.expires_at,
        }
        for c in person.certifications.all().order_by("-issued_at", "name")
    ]

    trainings = []
    for tr in person.training_records.select_related("training_course").all().order_by("-completed_at"):
        tc = tr.training_course
        trainings.append(
            {
                "course_name": tr.course_name,
                "completed_at": tr.completed_at,
                "training_course": (
                    {"id": tc.id, "category": getattr(tc, "category", None), "level": getattr(tc, "level", None)}
                    if tc is not None
                    else None
                ),
            }
        )

    return {
        "person_id": person.id,
        "name": f"{person.first_name} {person.last_name}".strip(),
        "email": person.email,
        "role": person.role,
        "is_team_lead": person.is_team_lead,
        "certifications": certs,
        "training": trainings,
    }


def machine_available(
    machine: Union[Machine, int],
    start,
    end,
    *,
    include_conflict: bool = False,
) -> Union[bool, Dict[str, Any]]:
    """Check if a machine is available in the [start, end) window.

    Args:
        machine: Machine instance or machine ID
        start: Start datetime (timezone-aware)
        end: End datetime (timezone-aware)
        include_conflict: If True, return dict with conflict details; if False, return bool

    Returns:
        - bool when include_conflict=False (True if available, False if conflict exists)
        - dict when include_conflict=True, with keys {available: bool, conflict: {...}|None}

    Example Input (simple):
        from datetime import datetime, timezone
        machine_available(
            machine=15,  # Machine ID
            start=datetime(2025, 11, 5, 10, 0, tzinfo=timezone.utc),
            end=datetime(2025, 11, 5, 12, 0, tzinfo=timezone.utc)
        )

    Example Output (simple):
        True  # Machine is available

    Example Input (with conflict details):
        machine_available(
            machine=laser_cutter_obj,  # Machine instance
            start=datetime(2025, 11, 5, 14, 0, tzinfo=timezone.utc),
            end=datetime(2025, 11, 5, 16, 0, tzinfo=timezone.utc),
            include_conflict=True
        )

    Example Output (available):
        {
            'available': True,
            'conflict': None
        }

    Example Output (conflict exists):
        {
            'available': False,
            'conflict': {
                'id': 87,
                'person_email': 'bob@example.com',
                'start': datetime(2025, 11, 5, 13, 0, tzinfo=timezone.utc),
                'end': datetime(2025, 11, 5, 15, 0, tzinfo=timezone.utc)
            }
        }
    """
    if isinstance(machine, Machine):
        machine_obj = machine
    else:
        machine_obj = Machine.objects.get(pk=machine)

    # Direct query instead of calling cmr.services.has_conflict
    conflict_exists = Reservation.objects.filter(
        machine=machine_obj,
        start__lt=end,
        end__gt=start,
    ).exists()

    if not include_conflict:
        return not conflict_exists

    conflict = None
    if conflict_exists:
        # Fetch a representative overlapping reservation
        conflict = (
            Reservation.objects.filter(machine=machine_obj, start__lt=end, end__gt=start)
            .order_by("start")
            .values("id", "person_email", "start", "end")
            .first()
        )

    return {"available": not conflict_exists, "conflict": conflict}
