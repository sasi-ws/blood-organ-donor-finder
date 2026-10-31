from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blood_requests.alerts import eligible_donors, send_alerts
from blood_requests.models import BloodRequest, DonorResponse, Notification
from donors.models import DonorProfile

User = get_user_model()


def make_donor(username, blood_group="O-", city="Colombo", last_donation=None, donor_type="blood"):
    user = User.objects.create_user(username, f"{username}@example.com", "pass12345")
    DonorProfile.objects.create(
        user=user,
        full_name=username,
        date_of_birth=date(1995, 1, 1),
        gender="male",
        blood_group=blood_group,
        donor_type=donor_type,
        city=city,
        district="Colombo",
        phone="0771110000",
        last_donation_date=last_donation,
        consent_given=True,
    )
    return user


def make_request(requester, blood_group="A+", city="Colombo"):
    return BloodRequest.objects.create(
        requester=requester,
        patient_name="Test Patient",
        blood_group=blood_group,
        units=2,
        hospital="Test Hospital",
        city=city,
        district="Colombo",
        urgency="critical",
        needed_by=timezone.now() + timedelta(days=1),
    )


class AlertMatchingTests(TestCase):
    def setUp(self):
        self.requester = User.objects.create_user("seeker", "s@example.com", "pass12345")

    def test_compatible_donor_in_same_city_is_alerted(self):
        make_donor("donor1", blood_group="O-")
        req = make_request(self.requester, blood_group="A+")
        self.assertEqual(send_alerts(req), 1)
        self.assertEqual(Notification.objects.count(), 1)

    def test_incompatible_blood_group_is_not_alerted(self):
        make_donor("donor1", blood_group="B+")
        req = make_request(self.requester, blood_group="A+")
        self.assertEqual(len(eligible_donors(req)), 0)

    def test_donor_inside_gap_is_not_alerted(self):
        make_donor("donor1", last_donation=date.today() - timedelta(days=10))
        req = make_request(self.requester)
        self.assertEqual(len(eligible_donors(req)), 0)

    def test_donor_outside_gap_is_alerted(self):
        make_donor("donor1", last_donation=date.today() - timedelta(days=200))
        req = make_request(self.requester)
        self.assertEqual(len(eligible_donors(req)), 1)

    def test_other_city_only_alerted_at_later_stages(self):
        make_donor("donor1", city="Negombo")
        req = make_request(self.requester, city="Colombo")
        self.assertEqual(len(eligible_donors(req, stage=1)), 0)
        self.assertEqual(len(eligible_donors(req, stage=2)), 1)

    def test_hidden_donor_is_not_alerted(self):
        donor = make_donor("donor1")
        DonorProfile.objects.filter(user=donor).update(hide_profile=True)
        req = make_request(self.requester)
        self.assertEqual(len(eligible_donors(req)), 0)

    def test_requester_is_never_alerted_about_own_request(self):
        make_donor("donor1")
        req = make_request(User.objects.get(username="donor1"))
        self.assertEqual(len(eligible_donors(req)), 0)


class PhonePrivacyTests(TestCase):
    def setUp(self):
        self.requester = User.objects.create_user("seeker", "s@example.com", "pass12345")
        self.other = User.objects.create_user("other", "o@example.com", "pass12345")
        self.donor = make_donor("donor1")
        self.req = make_request(self.requester)

    def test_phone_hidden_on_public_list(self):
        response = self.client.get(reverse("blood_requests:request_list"))
        self.assertNotContains(response, "0771110000")

    def test_other_user_cannot_open_offers_page(self):
        DonorResponse.objects.create(request=self.req, donor=self.donor, can_help=True)
        self.client.login(username="other", password="pass12345")
        url = reverse("blood_requests:offers_received", args=[self.req.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_requester_sees_phone_after_offer(self):
        DonorResponse.objects.create(request=self.req, donor=self.donor, can_help=True)
        self.client.login(username="seeker", password="pass12345")
        url = reverse("blood_requests:offers_received", args=[self.req.pk])
        self.assertContains(self.client.get(url), "0771110000")


class RequestFormTests(TestCase):
    def test_past_date_is_rejected(self):
        User.objects.create_user("seeker", "s@example.com", "pass12345")
        self.client.login(username="seeker", password="pass12345")
        past = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(reverse("blood_requests:post_request"), {
            "patient_name": "P", "blood_group": "A+", "blood_type": "whole", "units": 1,
            "hospital": "H", "city": "Colombo", "district": "Colombo",
            "needed_by": past, "urgency": "normal",
        })
        self.assertEqual(BloodRequest.objects.count(), 0)
        self.assertContains(response, "cannot be in the past")