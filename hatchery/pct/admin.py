from django.contrib import admin
from pct.models import Person, Certification, TrainingRecord, TrainingCourse


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'first_name', 'last_name', 'role', 'is_team_lead')
    list_filter = ('role', 'is_team_lead')
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'person', 'issued_at', 'expires_at')
    list_filter = ('issued_at', 'expires_at')
    search_fields = ('name', 'person__email')


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'person', 'completed_at', 'training_course')
    list_filter = ('completed_at',)
    search_fields = ('course_name', 'person__email')


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'level')
    list_filter = ('category', 'level')
    search_fields = ('name',)
