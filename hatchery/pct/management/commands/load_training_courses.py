from django.core.management.base import BaseCommand
from pct.models import TrainingCourse
from core import constants as const

COURSES = {
    'Laser': [
        (1, 'Laser Cutting Basics Training'),
        (2, 'Laser Cutter Rotary Training'),
        (2, 'Multi-Surface UV Printer Training'),
    ],
    'Vinyl': [
        (1, 'Vinyl Cutting Basics Training'),
        (2, 'Direct-to-Garment Printing Training'),
        (2, 'Sticker Printing Training'),
    ],
    'Woodworking': [
        (1, 'Woodworking Basics Training'),
        (2, 'Intermediate Woodworking Training'),
        (2, 'CNC Routing Training'),
        (3, 'Advanced Woodworking Training'),
    ],
    'Textile': [
        (1, 'Sewing Machine Basics Training'),
        (2, 'Embroidery Machine Training'),
    ],
    'Metalworking': [
        (1, 'Waterjet Cutting Training'),
    ],
    '3D Printing': [
        (1, 'Intro to 3D Printing'),
    ],
    'Electronics': [
        (2, 'High-Detail Resing 3D Printing Training'),
        (2, 'Multi-Material Training'),
        (3, 'Photo-Realistic 3D Printing Training'),
        (1, 'Circuitry Basics Training'),
        (1, 'Soldering Basics Training'),
        (2, 'Circuitry 2'),
    ],
}


class Command(BaseCommand):
    help = 'Load predefined training courses into the catalog.'

    def handle(self, *args, **options):
        created = 0
        for category, items in COURSES.items():
            if category not in const.MACHINE_TYPES:
                self.stdout.write(self.style.WARNING(f"Skipping unknown category '{category}'"))
                continue
            for level, name in items:
                _, was_created = TrainingCourse.objects.get_or_create(
                    name=name, category=category, level=level
                )
                if was_created:
                    created += 1
        self.stdout.write(self.style.SUCCESS(f"Loaded training courses. Created {created} new entries."))
