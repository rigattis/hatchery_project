from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from pct.models import Person
from core import constants as const

@receiver(user_signed_up)
def create_person_on_signup(sender, request, user, **kwargs):
    """Create a Person record after signup if it doesn't exist."""
    first = user.first_name or ""
    last = user.last_name or ""

    # Use user as the unique key
    person, created = Person.objects.get_or_create(
        user=user,
        defaults={
            "first_name": first,
            "last_name": last,
            "email": user.email,
            "role": const.ROLE_USER,
        }
    )

    if not created:
        # Ensure role stays valid
        if person.role not in const.ROLES:
            person.role = const.ROLE_USER
        # Update name/email from user if missing
        if not person.first_name:
            person.first_name = first
        if not person.last_name:
            person.last_name = last
        if not person.email:
            person.email = user.email
        person.save()

@receiver(user_logged_in)
def create_person_on_login(sender, request, user, **kwargs):
    """Ensure a Person exists on login."""
    person, created = Person.objects.get_or_create(
        user=user,
        defaults={
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "role": const.ROLE_USER,
        }
    )
    if not created:
        # Update missing fields
        updated = False
        if not person.first_name:
            person.first_name = user.first_name or ""
            updated = True
        if not person.last_name:
            person.last_name = user.last_name or ""
            updated = True
        if not person.email:
            person.email = user.email
            updated = True
        if updated:
            person.save()
