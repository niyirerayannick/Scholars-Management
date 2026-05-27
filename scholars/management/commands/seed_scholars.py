from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Profile
from scholars.models import Scholar


SAMPLES = [
    ("Amina", "Ndlovu", "Female", "STEM", "2022", "Bachelor", "Main Campus", "Engineering", "South African", "Undergraduate", True, False, 2026),
    ("Jacob", "Mensah", "Male", "Non-STEM", "2021", "Bachelor", "City Campus", "Humanities", "Ghanaian", "Undergraduate", True, False, 2025),
    ("Lerato", "Mokoena", "Female", "STEM", "2020", "Masters", "Main Campus", "Science", "South African", "Postgraduate", True, True, 2024),
    ("Grace", "Chirwa", "Female", "Non-STEM", "2019", "Masters", "North Campus", "Education", "Malawian", "Postgraduate", False, True, 2023),
    ("Samuel", "Okafor", "Male", "STEM", "2023", "Bachelor", "Main Campus", "Engineering", "Nigerian", "Undergraduate", True, False, 2027),
    ("Nadia", "Patel", "Female", "STEM", "2024", "PhD", "Medical Campus", "Health Sciences", "South African", "Postgraduate", True, False, 2028),
    ("Thabo", "Dlamini", "Male", "Non-STEM", "2020", "Bachelor", "City Campus", "Business", "Eswatini", "Undergraduate", False, False, 2024),
    ("Fatima", "Hassan", "Female", "STEM", "2021", "Masters", "Medical Campus", "Health Sciences", "Kenyan", "Postgraduate", True, True, 2025),
]


class Command(BaseCommand):
    help = "Create sample users and scholar records."

    def handle(self, *args, **options):
        User = get_user_model()
        users = [
            ("admin", "Admin", True),
            ("manager", Profile.PROGRAM_MANAGER, False),
            ("data", Profile.DATA_OFFICER, False),
            ("viewer", Profile.VIEWER, False),
        ]
        for username, role, is_superuser in users:
            user, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@mcfsp.local", "is_staff": is_superuser, "is_superuser": is_superuser})
            if created:
                user.set_password("Password123!")
                user.save()
            user.profile.role = role
            user.profile.save()
        for index, row in enumerate(SAMPLES, start=1):
            first, last, gender, category, cohort, level, campus, college, nationality, program_type, active, alumni, grad = row
            Scholar.objects.get_or_create(
                email=f"{first.lower()}.{last.lower()}@example.com",
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "gender": gender,
                    "student_no": f"SEED-{index:03d}",
                    "category": "Others",
                    "stem_category": category,
                    "cohort": cohort,
                    "level_of_study": level,
                    "campus": campus,
                    "college": college,
                    "nationality": nationality,
                    "program_type": program_type,
                    "is_active": active,
                    "is_alumni": alumni,
                    "expected_graduation_year": grad,
                    "graduation_year": grad,
                    "class_year": str(grad),
                    "intake": "January",
                    "phone": f"+27 11 555 01{index:02d}",
                    "remarks": "Seed record for dashboard and report validation.",
                },
            )
        self.stdout.write(self.style.SUCCESS("Seeded users and scholars. Password for sample users: Password123!"))
