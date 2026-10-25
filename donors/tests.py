from django.test import SimpleTestCase
from datetime import date, timedelta

from .eligibility import days_until_eligible, next_eligible_date

from .compatibility import CAN_RECEIVE_FROM, compatible_donor_groups, match_label


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