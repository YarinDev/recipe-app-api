"""
Test for the Django admin modifications we made in app/core/admin.py:
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Tests for Django admin"""

    def setUp(self):
        """Create user and client for http requests to admin site to use in tests below"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123",
            name="Test User",
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        # generate url for list user page
        url = reverse("admin:core_user_changelist")
        # perform http get on url
        res = self.client.get(url)
        # assert that response contains status code 200
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that the edit user page works"""
        # generate url for edit user page
        url = reverse("admin:core_user_change", args=[self.user.id])
        # perform http get on url
        res = self.client.get(url)
        # assert that response contains status code 200
        self.assertEqual(res.status_code, 200)
