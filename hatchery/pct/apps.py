from django.apps import AppConfig


class PctConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pct'
    verbose_name = 'People, Certifications, and Training'
    def ready(self):
        import pct.signals
