from django.db import models
from django.core.exceptions import ValidationError
from core import constants as const
from django.contrib.auth.models import User


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50,
        choices=[(r, r) for r in const.ROLES],
        default=const.ROLE_USER,
    )
    # Team Lead is only meaningful when role is Team Member
    is_team_lead = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        # Enforce that Team Lead flag only applies to Team Members
        if self.is_team_lead and self.role != const.TEAM_LEAD_ELIGIBLE_ROLE:
            raise ValidationError({
                'is_team_lead': 'Team Lead can only be set when role is Team Member.'
            })

    def save(self, *args, **kwargs):
        # Ensure model validation runs on save
        self.full_clean()
        return super().save(*args, **kwargs)


class Certification(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issued_at = models.DateField()
    expires_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.person})"


class TrainingRecord(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='training_records')
    course_name = models.CharField(max_length=200)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_name} - {self.person}"


class TrainingCourse(models.Model):
    """Catalog of training/certification courses by category and level."""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=[(t, t) for t in const.MACHINE_TYPES])
    level = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('name', 'category', 'level')
        ordering = ['category', 'level', 'name']

    def __str__(self):
        return f"Lvl {self.level} - {self.name} ({self.category})"

# Backward-compatible link from a record to a cataloged course (optional)
TrainingRecord.add_to_class(
    'training_course',
    models.ForeignKey('TrainingCourse', on_delete=models.SET_NULL, null=True, blank=True, related_name='records')
)
