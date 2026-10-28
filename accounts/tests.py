from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="testdonor", email="t@example.com",
            password="StrongPass123", role="donor",
        )

    def test_register_donor_creates_user(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newdonor",
            "email": "d@example.com",
            "role": "donor",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "agree": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(username="newdonor").role, "donor")

    def test_register_seeker_creates_profile(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newseeker",
            "email": "new@example.com",
            "role": "seeker",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "full_name": "Test Seeker",
            "seeker_type": "family",
            "phone": "077 111 0002",
            "city": "Colombo",
            "district": "Colombo",
            "agree": "on",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newseeker")
        self.assertEqual(user.role, "seeker")
        self.assertEqual(user.seeker_profile.city, "Colombo")

    def test_seeker_without_details_is_rejected(self):
        self.client.post(reverse("accounts:register"), {
            "username": "emptyseeker",
            "email": "e@example.com",
            "role": "seeker",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
            "agree": "on",
        })
        self.assertFalse(User.objects.filter(username="emptyseeker").exists())

    def test_register_requires_agreement(self):
        self.client.post(reverse("accounts:register"), {
            "username": "noagree",
            "email": "x@example.com",
            "role": "donor",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })
        self.assertFalse(User.objects.filter(username="noagree").exists())

    def test_password_is_hashed(self):
        self.assertNotEqual(self.user.password, "StrongPass123")

    def test_login_works(self):
        self.assertTrue(
            self.client.login(username="testdonor", password="StrongPass123")
        )

    def test_login_locks_after_five_failures(self):
        url = reverse("accounts:login")
        for _ in range(5):
            self.client.post(url, {"username": "testdonor", "password": "wrong"})
        # Even the correct password is blocked now
        self.client.post(url, {"username": "testdonor", "password": "StrongPass123"})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_delete_account_removes_user(self):
        self.client.login(username="testdonor", password="StrongPass123")
        self.client.post(reverse("accounts:delete"))
        self.assertFalse(User.objects.filter(username="testdonor").exists())

    def test_delete_requires_login(self):
        response = self.client.get(reverse("accounts:delete"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)