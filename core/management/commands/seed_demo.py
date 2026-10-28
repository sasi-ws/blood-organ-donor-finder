"""Fill the database with FICTIONAL demo data (FR-ADM-03).

Run:  py manage.py seed_demo
Safe to rerun: it removes old demo data (usernames starting "demo_") first.
All names and phone numbers are fake. Never use real data (SRS 2.5).
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import SeekerProfile, User
from blood_requests.models import BloodRequest, DonorResponse, Notification
from donors.models import DonorProfile

PREFIX = "demo_"
PASSWORD = "Demo12345!"  # same fake password for every demo account

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
# Weighted so O+ and A+ are common and AB- is rare, like real life
WEIGHTS = [28, 4, 22, 3, 6, 1, 32, 4]

CITIES = [
    ("Colombo", "Colombo"),
    ("Negombo", "Gampaha"),
    ("Gampaha", "Gampaha"),
    ("Kandy", "Kandy"),
    ("Galle", "Galle"),
]
FIRST = ["Kasuni", "Anjali", "Nimal", "Madhavi", "Dilan", "Sachini", "Tharindu",
         "Ishara", "Kamal", "Nadeesha", "Ruwan", "Piumi", "Chamara", "Hiruni",
         "Sampath", "Dinesh", "Malsha", "Janaka", "Thilini", "Asanka"]
LAST = ["Silva", "Perera", "Fernando", "Jayasinghe", "Peiris", "Rathnayake",
        "Wickrama", "Gomes", "Bandara", "Senanayake", "Wijesinghe", "Herath"]
HOSPITALS = {
    "Colombo": "General Hospital",
    "Negombo": "Negombo Base Hospital",
    "Gampaha": "Gampaha District Hospital",
    "Kandy": "Kandy Teaching Hospital",
    "Galle": "Karapitiya Hospital",
}


class Command(BaseCommand):
    help = "Create fictional demo donors, seekers, requests and notifications."

    def handle(self, *args, **options):
        random.seed(42)  # same data every run
        now = timezone.now()

        # 1. Remove old demo data (cascade removes profiles, requests, etc.)
        deleted, _ = User.objects.filter(username__startswith=PREFIX).delete()
        if deleted:
            self.stdout.write(f"Removed {deleted} old demo records.")

        # 2. Seekers (3)
        seekers = []
        for i in range(1, 4):
            city, district = CITIES[i % len(CITIES)]
            u = User.objects.create_user(
                username=f"{PREFIX}seeker{i}", email=f"seeker{i}@example.com",
                password=PASSWORD, role="seeker")
            SeekerProfile.objects.create(
                user=u, full_name=f"{random.choice(FIRST)} {random.choice(LAST)}",
                seeker_type=["patient", "family", "hospital"][i - 1],
                hospital=HOSPITALS[city], phone=f"077 222 {i:04d}",
                city=city, district=district)
            seekers.append(u)

        # 3. Donors (50)
        donors = []
        for i in range(1, 51):
            city, district = CITIES[(i - 1) % len(CITIES)]
            group = random.choices(BLOOD_GROUPS, weights=WEIGHTS)[0]
            u = User.objects.create_user(
                username=f"{PREFIX}donor{i}", email=f"donor{i}@example.com",
                password=PASSWORD, role="donor")

            # Mix of situations to test every rule
            last_donation = None
            if i % 5 == 0:      # inside the 120-day gap (must be hidden)
                last_donation = (now - timedelta(days=random.randint(10, 100))).date()
            elif i % 3 == 0:    # donated long ago (eligible)
                last_donation = (now - timedelta(days=random.randint(130, 400))).date()
            # others: never donated (eligible)

            DonorProfile.objects.create(
                user=u,
                full_name=f"{random.choice(FIRST)} {random.choice(LAST)}",
                date_of_birth=(now - timedelta(days=365 * random.randint(19, 54))).date(),
                gender=random.choice(["Male", "Female"]),
                blood_group=group,
                donor_type=random.choice(["blood", "blood", "platelets", "both"]),
                city=city, district=district,
                phone=f"077 111 {i:04d}",        # clearly fake
                last_donation_date=last_donation,
                is_verified=(i % 2 == 0),         # half verified
                hide_profile=(i % 11 == 0),       # a few paused
                available_until=(now + timedelta(hours=random.randint(2, 20)))
                                if i % 7 == 0 else None,   # "available today"
                travel_city="Kandy" if i == 13 else "",
                consent_given=True, consent_date=now)
            donors.append(u)

        # 4. Blood requests (6): normal, urgent, critical
        samples = [
            ("O-", "whole", 2, "Colombo", "critical", 6, "Needed urgently for surgery."),
            ("A+", "platelets", 1, "Colombo", "critical", 20, "Dengue patient."),
            ("B+", "whole", 1, "Kandy", "urgent", 20, ""),
            ("AB-", "whole", 1, "Galle", "normal", 60, ""),
            ("O+", "whole", 3, "Negombo", "urgent", 18, ""),
            ("A-", "whole", 1, "Gampaha", "normal", 70, ""),
        ]
        for n, (group, btype, units, city, urgency, hours, notes) in enumerate(samples):
            district = dict(CITIES)[city]
            req = BloodRequest.objects.create(
                requester=seekers[n % len(seekers)],
                patient_name=f"Patient {n + 1}", blood_group=group,
                units=units, blood_type=btype, hospital=HOSPITALS[city],
                city=city, district=district, urgency=urgency,
                needed_by=now + timedelta(hours=hours), notes=notes,
                status="open", alert_stage=1 + (n % 3))
            # one donor already offered on the first request
            if n == 0:
                DonorResponse.objects.create(
                    request=req, donor=donors[0], can_help=True, viewed_at=now)

        # 5. A few notifications for the first donor
        for msg in ["Critical request near you: O- needed at General Hospital.",
                    "A seeker asked to contact you.",
                    "You can donate again soon."]:
            Notification.objects.create(user=donors[0], message=msg, link="/")

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready: {len(donors)} donors, {len(seekers)} seekers, "
            f"{len(samples)} requests."))
        self.stdout.write(f"Log in as demo_donor1 / demo_seeker1, password: {PASSWORD}")