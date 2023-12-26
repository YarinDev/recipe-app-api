"""
Test for the user api.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")


def create_user(**params):
    """Helper function to createa and return a new user"""
    return get_user_model().objects.create_user(**params)


# public user api tests - anyone can access these endpoints
class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user with valid payload is successful"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        # make a post request to the create user url with the payload
        res = self.client.post(CREATE_USER_URL, payload)

        # assert that the response status code is 201 (success response code for creating an object in the db)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # retrieve the user object from the db using the email
        user = get_user_model().objects.get(email=payload["email"])
        # assert that the password of the user is the same as the password in the payload
        self.assertTrue(user.check_password(payload["password"]))
        # assert that the password is not returned in the response
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error is raised if user with email already exists"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        # create a user with the payload
        create_user(**payload)
        # make a post request to the create user url with the payload
        res = self.client.post(CREATE_USER_URL, payload)

        # assert that the response status code is 400 (bad request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_short_password_error(self):
        """Test error is raised if password is too short"""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test Name",
        }
        # make a post request to the create user url with the payload
        res = self.client.post(CREATE_USER_URL, payload)

        # assert that the response status code is 400 (bad request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # assert that the user was not created
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        # confirm that the user does not exist
        self.assertFalse(user_exists)
