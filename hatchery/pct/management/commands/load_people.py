from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from core import constants as const
from pct import methods
from pct.models import Person, TrainingCourse

EXAMPLE = (
    "first_name,last_name,email,role,is_team_lead,certifications,training\n"
    "Alex,Rivera,alex@example.com,User,false,,'Intro to 3D Printing; Laser Cutting Basics Training'\n"
    "Jamie,Chen,jamie@example.com,Team Member,true,Laser Safety,Intro to 3D Printing\n"
)

ROLE_TO_FUNC = {
    const.ROLE_USER: methods.add_user,
    const.ROLE_COLLABORATOR: methods.add_collaborator,
    const.ROLE_TEAM_MEMBER: methods.add_team_member,
    const.ROLE_STAFF: methods.add_staff,
}


class Command(BaseCommand):
    help = (
        "Load or update people and training from a CSV file. Columns: "
        "first_name,last_name,email,role,is_team_lead,certifications,training. "
        "'certifications' and 'training' are semicolon-separated."
    )

    def add_arguments(self, parser):
        parser.add_argument("--file", help="Path to CSV file")
        parser.add_argument("--example", action="store_true", help="Print example CSV and exit")
        parser.add_argument("--dry-run", action="store_true", help="Parse and validate without saving")

    def handle(self, *args, **options):
        if options.get("example"):
            self.stdout.write(EXAMPLE)
            return

        file_path = options.get("file")
        if not file_path:
            raise CommandError("--file is required (unless using --example)")
        
        path = Path(file_path).expanduser()
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        dry = options.get("dry_run", False)
        created = updated = cert_count = train_count = 0

        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            required = {"first_name", "last_name", "email", "role"}
            missing_cols = required - set(reader.fieldnames or [])
            if missing_cols:
                raise CommandError(f"Missing required columns: {sorted(missing_cols)}")

            for row in reader:
                fn = (row.get("first_name") or "").strip()
                ln = (row.get("last_name") or "").strip()
                email = (row.get("email") or "").strip()
                role = (row.get("role") or "").strip()
                is_lead = (row.get("is_team_lead") or "").strip().lower() in {"1", "true", "yes", "y"}

                if role not in const.ROLES:
                    self.stdout.write(self.style.WARNING(f"Skipping {email}: invalid role '{role}'."))
                    continue

                person = Person.objects.filter(email=email).first()

                try:
                    if dry:
                        # Validate as if creating/updating
                        if person is None:
                            fnc = ROLE_TO_FUNC[role]
                            p = fnc(fn, ln, email) if role != const.ROLE_TEAM_MEMBER else methods.add_team_member(fn, ln, email, is_lead)
                        else:
                            person.first_name = fn
                            person.last_name = ln
                            person.role = role
                            person.is_team_lead = is_lead if role == const.ROLE_TEAM_MEMBER else False
                            person.full_clean()
                    else:
                        if person is None:
                            fnc = ROLE_TO_FUNC[role]
                            if role == const.ROLE_TEAM_MEMBER:
                                person = methods.add_team_member(fn, ln, email, is_lead)
                            else:
                                person = fnc(fn, ln, email)
                            created += 1
                        else:
                            person.first_name = fn
                            person.last_name = ln
                            person.role = role
                            person.is_team_lead = is_lead if role == const.ROLE_TEAM_MEMBER else False
                            person.full_clean()
                            person.save()
                            updated += 1
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Person error for {email}: {e}"))
                    continue

                # Certifications (semicolon separated names)
                certs = [c.strip() for c in (row.get("certifications") or "").split(";") if c.strip()]
                for cname in certs:
                    if dry:
                        cert_count += 1
                    else:
                        from datetime import date
                        methods.add_certification(person, cname, issued_at=date.today())
                        cert_count += 1

                # Training (semicolon separated names); try catalog match first
                trainings = [t.strip() for t in (row.get("training") or "").split(";") if t.strip()]
                for tname in trainings:
                    if dry:
                        train_count += 1
                        continue
                    tc = TrainingCourse.objects.filter(name=tname).first()
                    if tc is not None:
                        methods.add_training(person, training_course=tc)
                    else:
                        methods.add_training(person, course_name=tname)
                    train_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"load_people complete. Created: {created}, Updated: {updated}, "
            f"Certifications: {cert_count}, Training records: {train_count}"
        ))
