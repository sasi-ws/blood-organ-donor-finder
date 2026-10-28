from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from .quiz import check_quiz

from .compatibility import CAN_RECEIVE_FROM, compatible_donor_groups, match_label
from .eligibility import days_until_eligible, next_eligible_date
from .forms import DonorProfileForm, calculate_age
from .models import DonorProfile


class CompatibilityTests(SimpleTestCase):
    def test_a_positive_accepts_o_negative(self):
        self.assertIn("O-", compatible_donor_groups("A+"))

    def test_o_negative_only_from_o_negative(self):
        self.assertEqual(compatible_donor_groups("O-"), ["O-"])

    def test_ab_positive_accepts_all_groups(self):
        self.assertEqual(len(compatible_donor_groups("AB+")), 8)

    def test_a_negative_does_not_accept_a_positive(self):
        self.assertNotIn("A+", compatible_donor_groups("A-"))

    def test_every_group_accepts_itself(self):
        for group, donors in CAN_RECEIVE_FROM.items():
            self.assertIn(group, donors)

    def test_labels(self):
        self.assertEqual(match_label("A+", "A+"), "Exact match")
        self.assertEqual(match_label("A+", "O-"), "Compatible")


class EligibilityTests(SimpleTestCase):
    today = date(2026, 10, 25)

    def test_never_donated_is_eligible(self):
        self.assertIsNone(next_eligible_date(None))
        self.assertEqual(days_until_eligible(None, "blood", self.today), 0)

    def test_donated_10_days_ago_has_110_days_left(self):
        last = self.today - timedelta(days=10)
        self.assertEqual(days_until_eligible(last, "blood", self.today), 110)

    def test_exactly_120_days_ago_is_eligible(self):
        last = self.today - timedelta(days=120)
        self.assertEqual(days_until_eligible(last, "blood", self.today), 0)

    def test_next_eligible_date_is_last_plus_gap(self):
        last = date(2026, 8, 14)
        self.assertEqual(next_eligible_date(last, "blood"), date(2026, 12, 12))

    def test_platelet_gap_is_shorter(self):
        last = self.today - timedelta(days=20)
        self.assertEqual(days_until_eligible(last, "platelets", self.today), 0)
        self.assertEqual(days_until_eligible(last, "blood", self.today), 100)


def birthday_years_ago(years):
    """Date of birth (as text) for someone who is exactly this many years old."""
    today = date.today()
    return date(today.year - years, today.month, min(today.day, 28)).isoformat()


def valid_form_data(**overrides):
    """A fully valid set of form data, with fake values."""
    data = {
        "full_name": "Test Donor",
        "date_of_birth": birthday_years_ago(25),
        "gender": "Female",
        "blood_group": "A+",
        "donor_type": "blood",
        "city": "Colombo",
        "district": "Colombo",
        "phone": "0771110001",
        "last_donation_date": "",
        "consent_given": True,
        "self_declaration": True,
    }
    data.update(overrides)
    return data


class AgeAndFormTests(TestCase):
    def test_calculate_age(self):
        today = date.today()
        dob = date(today.year - 30, today.month, min(today.day, 28))
        self.assertEqual(calculate_age(dob), 30)

    def test_valid_adult_is_accepted(self):
        self.assertTrue(DonorProfileForm(valid_form_data()).is_valid())

    def test_17_year_old_is_rejected(self):
        data = valid_form_data(date_of_birth=birthday_years_ago(17))
        self.assertFalse(DonorProfileForm(data).is_valid())

    def test_first_time_donor_over_55_is_rejected(self):
        data = valid_form_data(date_of_birth=birthday_years_ago(56), last_donation_date="")
        self.assertFalse(DonorProfileForm(data).is_valid())

    def test_experienced_donor_aged_56_is_accepted(self):
        last = (date.today() - timedelta(days=200)).isoformat()
        data = valid_form_data(date_of_birth=birthday_years_ago(56), last_donation_date=last)
        self.assertTrue(DonorProfileForm(data).is_valid())

    def test_over_60_is_rejected(self):
        last = (date.today() - timedelta(days=200)).isoformat()
        data = valid_form_data(date_of_birth=birthday_years_ago(61), last_donation_date=last)
        self.assertFalse(DonorProfileForm(data).is_valid())

    def test_missing_consent_is_rejected(self):
        self.assertFalse(DonorProfileForm(valid_form_data(consent_given=False)).is_valid())

    def test_future_last_donation_date_is_rejected(self):
        future = (date.today() + timedelta(days=5)).isoformat()
        self.assertFalse(DonorProfileForm(valid_form_data(last_donation_date=future)).is_valid())

    def test_bad_phone_is_rejected(self):
        self.assertFalse(DonorProfileForm(valid_form_data(phone="12345")).is_valid())


class AvailableTodayTests(SimpleTestCase):
    def test_available_while_within_24_hours(self):
        donor = DonorProfile(available_until=timezone.now() + timedelta(hours=5))
        self.assertTrue(donor.is_available_today)

    def test_not_available_after_expiry(self):
        donor = DonorProfile(available_until=timezone.now() - timedelta(minutes=1))
        self.assertFalse(donor.is_available_today)

    def test_not_available_when_never_set(self):
        self.assertFalse(DonorProfile().is_available_today)
class TravelModeTests(SimpleTestCase):
    def test_home_city_when_travel_mode_is_off(self):
        donor = DonorProfile(city="Colombo", travel_city="")
        self.assertEqual(donor.current_city, "Colombo")

    def test_travel_city_when_travel_mode_is_on(self):
        donor = DonorProfile(city="Colombo", travel_city="Kandy")
        self.assertEqual(donor.current_city, "Kandy")

    def test_spaces_only_counts_as_off(self):
        donor = DonorProfile(city="Colombo", travel_city="   ")
        self.assertEqual(donor.current_city, "Colombo")

class QuizTests(SimpleTestCase):
    today = date(2026, 10, 25)

    def run_quiz(self, **overrides):
        answers = dict(
            age=30, weight_kg=60, last_donation_date=None,
            feeling_ill=False, travelled_abroad=False, recent_tattoo=False,
            today=self.today,
        )
        answers.update(overrides)
        return check_quiz(**answers)

    def test_no_problems(self):
        self.assertEqual(self.run_quiz(), [])

    def test_too_young(self):
        self.assertTrue(self.run_quiz(age=17))

    def test_first_time_donor_over_55(self):
        self.assertTrue(self.run_quiz(age=56))

    def test_experienced_donor_aged_56_is_fine(self):
        last = self.today - timedelta(days=200)
        self.assertEqual(self.run_quiz(age=56, last_donation_date=last), [])

    def test_underweight(self):
        self.assertTrue(self.run_quiz(weight_kg=48))

    def test_inside_donation_gap(self):
        last = self.today - timedelta(days=30)
        self.assertTrue(self.run_quiz(last_donation_date=last))

    def test_ill_travel_and_tattoo_each_add_a_note(self):
        self.assertEqual(len(self.run_quiz(feeling_ill=True, travelled_abroad=True, recent_tattoo=True)), 3)