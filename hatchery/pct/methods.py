"""Convenience methods to create PCT entities (people, certifications, training records).

Each helper accepts either model instances or primary key IDs for related objects.
They use the shared role constants from hatchery.core.constants and enforce
Team Lead eligibility (only for Team Members).
"""
from __future__ import annotations

from typing import Optional, Sequence, Union

from django.core.exceptions import ValidationError
from django.utils import timezone

from core import constants as const
from pct.models import (
    Person,
    Certification,
    TrainingRecord,
    TrainingCourse,
)


def _get_instance(model, obj_or_id):
    if isinstance(obj_or_id, model):
        return obj_or_id
    return model.objects.get(pk=obj_or_id)


# ---- Person helpers ---------------------------------------------------------

def _add_person(
    first_name: str,
    last_name: str,
    email: str,
    role: str,
    is_team_lead: bool = False,
) -> Person:
    if role not in const.ROLES:
        raise ValidationError({"role": f"Invalid role: {role}"})
    person = Person(
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        is_team_lead=is_team_lead,
    )
    # Will enforce team lead eligibility via model validation
    person.full_clean()
    person.save()
    return person


def add_user(first_name: str, last_name: str, email: str) -> Person:
    """Create a Person with role User."""
    return _add_person(first_name, last_name, email, const.ROLE_USER, is_team_lead=False)


def add_collaborator(first_name: str, last_name: str, email: str) -> Person:
    """Create a Person with role Collaborator."""
    return _add_person(first_name, last_name, email, const.ROLE_COLLABORATOR, is_team_lead=False)


def add_team_member(
    first_name: str,
    last_name: str,
    email: str,
    is_team_lead: bool = False,
) -> Person:
    """Create a Person with role Team Member, optionally flagged as Team Lead."""
    return _add_person(first_name, last_name, email, const.ROLE_TEAM_MEMBER, is_team_lead=is_team_lead)


def add_staff(first_name: str, last_name: str, email: str) -> Person:
    """Create a Person with role Staff."""
    return _add_person(first_name, last_name, email, const.ROLE_STAFF, is_team_lead=False)


def add_team_lead(first_name: str, last_name: str, email: str) -> Person:
    """Create a Person as a Team Member and mark them Team Lead."""
    return add_team_member(first_name, last_name, email, is_team_lead=True)


# ---- Certification & Training ---------------------------------------------

def add_certification(
    person: Union[Person, int],
    name: str,
    issued_at,
    expires_at=None,
) -> Certification:
    """Create a Certification for a person."""
    person_obj = _get_instance(Person, person)
    cert = Certification(person=person_obj, name=name, issued_at=issued_at, expires_at=expires_at)
    cert.full_clean()
    cert.save()
    return cert


def add_training(
    person: Union[Person, int],
    course_name: Optional[str] = None,
    training_course: Optional[Union[TrainingCourse, int]] = None,
    completed_at=None,
) -> TrainingRecord:
    """Create a TrainingRecord for a person.

    Provide either course_name or training_course. If only training_course is
    provided, course_name will be auto-populated from it. completed_at defaults
    to now if not provided (matching model auto_now_add behavior).
    """
    if not course_name and not training_course:
        raise ValidationError("Provide either course_name or training_course.")

    person_obj = _get_instance(Person, person)
    tc_obj = _get_instance(TrainingCourse, training_course) if training_course is not None else None

    name_to_use = course_name or (tc_obj.name if tc_obj else None)
    if not name_to_use:
        raise ValidationError({"course_name": "Could not determine course_name from inputs."})

    record = TrainingRecord(
        person=person_obj,
        course_name=name_to_use,
        training_course=tc_obj,
    )
    if completed_at is not None:
        record.completed_at = completed_at
    # full_clean will ensure any model-level constraints
    record.full_clean()
    record.save()
    return record
