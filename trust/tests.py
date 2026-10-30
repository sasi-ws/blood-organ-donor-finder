from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from blood_requests.models import Notification

from donors.models import DonorProfile

from .keywords import find_scam_words
from .models import ContactRequest

User = get_user_model()

PHONE = "0771110001"   # fictional number used in the tests
PASSWORD = "pass12345"


class ScamKeywordTests(SimpleTestCase):
    def test_finds_money_words(self):
        self.assertEqual(find_scam_words("I will pay you Rs 5000 cash"), ["cash", "pay", "rs"])

    def test_clean_message_is_not_flagged(self):
        self.assertEqual(find_scam_words("I need O+ blood for my father at General Hospital"), [])

    def test_whole_words_only(self):
        self.assertEqual(find_scam_words("Come in two hours"), [])

    def test_empty_text(self):
        self.assertEqual(find_scam_words(""), [])


def make_donor(username, name, phone=PHONE):
    """Create a donor user plus an eligible, visible donor profile."""
    user = User.objects.create_user(username, password=PASSWORD, role="donor")
    profile = DonorProfile.objects.create(
        user=user,
        full_name=name,
        date_of_birth=date(1990, 1, 1),
        gender="Male",
        blood_group="O+",
        donor_type="blood",
        city="Colombo",
        district="Colombo",
        phone=phone,
        consent_given=True,
    )
    return user, profile


class PrivacyTests(TestCase):
    """Phone numbers stay hidden until the donor accepts (BR-03, NFR-SEC-05)."""

    def setUp(self):
        self.seeker = User.objects.create_user("seeker1", password=PASSWORD, role="seeker")
        self.other_seeker = User.objects.create_user("seeker2", password=PASSWORD, role="seeker")
        self.donor_user, self.donor = make_donor("donor1", "Janaka Test")
        self.req = ContactRequest.objects.create(
            seeker=self.seeker, donor=self.donor, message="Need O+ blood"
        )

    def test_phone_hidden_while_pending(self):
        self.client.force_login(self.seeker)
        response = self.client.get(reverse("trust:sent_requests"))
        self.assertContains(response, "Janaka Test")
        self.assertNotContains(response, PHONE)

    def test_phone_shown_after_accept(self):
        self.req.status = "accepted"
        self.req.save()
        self.client.force_login(self.seeker)
        response = self.client.get(reverse("trust:sent_requests"))
        self.assertContains(response, PHONE)

    def test_phone_hidden_after_decline(self):
        self.req.status = "declined"
        self.req.save()
        self.client.force_login(self.seeker)
        response = self.client.get(reverse("trust:sent_requests"))
        self.assertNotContains(response, PHONE)

    def test_other_seeker_cannot_see_the_phone(self):
        self.req.status = "accepted"
        self.req.save()
        self.client.force_login(self.other_seeker)
        response = self.client.get(reverse("trust:sent_requests"))
        self.assertNotContains(response, PHONE)
        self.assertNotContains(response, "Need O+ blood")

    def test_search_results_never_show_the_phone(self):
        response = self.client.get(
            reverse("donors:search"), {"blood_group": "O+", "city": "Colombo"}
        )
        self.assertContains(response, "Janaka Test")   # the donor is listed...
        self.assertNotContains(response, PHONE)        # ...but the phone is not


class AccessControlTests(TestCase):
    """Users can act only on their own data (NFR-SEC-03)."""

    def setUp(self):
        self.seeker = User.objects.create_user("seeker1", password=PASSWORD, role="seeker")
        self.donor_user, self.donor = make_donor("donor1", "Donor One", phone="0771110001")
        self.other_user, self.other_donor = make_donor("donor2", "Donor Two", phone="0771110002")
        self.req = ContactRequest.objects.create(
            seeker=self.seeker, donor=self.donor, message="Need O+ blood"
        )

    def test_donor_cannot_answer_another_donors_request(self):
        self.client.force_login(self.other_user)   # donor2 tries to answer donor1's request
        response = self.client.post(reverse("trust:accept_request", args=[self.req.id]))
        self.assertEqual(response.status_code, 404)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "pending")

    def test_right_donor_can_accept(self):
        self.client.force_login(self.donor_user)
        self.client.post(reverse("trust:accept_request", args=[self.req.id]))
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "accepted")

    def test_accepting_needs_post_not_a_link(self):
        self.client.force_login(self.donor_user)
        response = self.client.get(reverse("trust:accept_request", args=[self.req.id]))
        self.assertEqual(response.status_code, 405)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "pending")

    def test_donor_account_cannot_send_contact_requests(self):
        self.client.force_login(self.donor_user)
        self.client.post(
            reverse("trust:request_contact", args=[self.other_donor.id]),
            {"message": "Hello"},
        )
        # still only the one request created in setUp
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_logged_out_visitors_are_sent_to_login(self):
        urls = [
            reverse("trust:sent_requests"),
            reverse("trust:my_requests"),
            reverse("trust:request_contact", args=[self.donor.id]),
            reverse("trust:report_user", args=[self.donor.id]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("login", response["Location"])

    def test_admin_pages_are_not_open_to_normal_users(self):
        self.client.force_login(self.seeker)
        response = self.client.get("/admin/trust/contactrequest/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response["Location"])


class RateLimitAndCsrfTests(TestCase):
    def setUp(self):
        self.seeker = User.objects.create_user("seeker1", password=PASSWORD, role="seeker")
        self.donor_user, self.donor = make_donor("donor1", "Donor One", phone="0771110001")
        self.other_user, self.other_donor = make_donor("donor2", "Donor Two", phone="0771110002")

    def test_daily_limit_of_10_requests(self):
        for i in range(10):
            ContactRequest.objects.create(
                seeker=self.seeker, donor=self.donor, message=f"msg {i}", status="declined"
            )
        self.client.force_login(self.seeker)
        self.client.post(
            reverse("trust:request_contact", args=[self.other_donor.id]),
            {"message": "One too many"},
        )
        self.assertEqual(ContactRequest.objects.count(), 10)   # the 11th was refused

    def test_post_without_csrf_token_is_rejected(self):
        strict_client = Client(enforce_csrf_checks=True)
        strict_client.force_login(self.seeker)
        response = strict_client.post(
            reverse("trust:request_contact", args=[self.donor.id]),
            {"message": "No token"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ContactRequest.objects.count(), 0)
class NotificationTests(TestCase):
    """The seeker is told when a donor answers (FR-CON-05)."""

    def setUp(self):
        self.seeker = User.objects.create_user("seeker1", password=PASSWORD, role="seeker")
        self.other_seeker = User.objects.create_user("seeker2", password=PASSWORD, role="seeker")
        self.donor_user, self.donor = make_donor("donor1", "Janaka Test")
        self.req = ContactRequest.objects.create(
            seeker=self.seeker, donor=self.donor, message="Need O+ blood"
        )

    def test_accept_notifies_the_seeker(self):
        self.client.force_login(self.donor_user)
        self.client.post(reverse("trust:accept_request", args=[self.req.id]))
        note = Notification.objects.get(user=self.seeker)
        self.assertIn("accepted", note.message)
        self.assertFalse(note.is_read)

    def test_decline_notifies_the_seeker_without_the_donor_name(self):
        self.client.force_login(self.donor_user)
        self.client.post(reverse("trust:decline_request", args=[self.req.id]))
        note = Notification.objects.get(user=self.seeker)
        self.assertIn("declined", note.message)
        self.assertNotIn("Janaka", note.message)

    def test_nobody_else_is_notified(self):
        self.client.force_login(self.donor_user)
        self.client.post(reverse("trust:accept_request", args=[self.req.id]))
        self.assertEqual(Notification.objects.filter(user=self.other_seeker).count(), 0)