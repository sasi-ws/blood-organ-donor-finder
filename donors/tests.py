from django.test import SimpleTestCase

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