"""
Test for the user api.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
#
TOKEN_URL = reverse("user:token")
# me url is the url for the endpoint that returns the authenticated user
ME_URL = reverse("user:me")


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

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-user-password123",
        }
        # create a user with the user details
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        # make a post request to the token url with the payload
        res = self.client.post(TOKEN_URL, payload)

        # assert that the response status code is 200 (success)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created if invalid credentials are given"""
        create_user(email="test@example.com", password="goodpass")

        payload = payload = {
            "email": "test@example.com",
            "password": "badpass",
        }
        # make a post request to the token url with the payload
        res = self.client.post(TOKEN_URL, payload)

        # assert that the response does not contain a token
        self.assertNotIn("token", res.data)

        # assert that the response status code is 400 (bad request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test that a token is not created if password is blank"""
        payload = {
            "email": "test@example.com",
            "password": "",
        }
        # make a post request to the token url with the payload
        res = self.client.post(TOKEN_URL, payload)

        # assert that the response does not contain a token
        self.assertNotIn("token", res.data)

        # assert that the response status code is 400 (bad request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        # make a get request to the me url
        res = self.client.get(ME_URL)

        # assert that the response status code is 401 (unauthorized)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# private user api tests - only authenticated users can access these endpoints
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user_details = create_user(
            email="test@example.com",
            password="testpass123",
            name="Test Name",
        )
        self.client = APIClient()
        # force authenticate the client
        self.client.force_authenticate(user=self.user_details)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        # make a get request to the me url
        res = self.client.get(ME_URL)

        # assert that the response status code is 200 (success)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # assert that the response data matches the user details
        self.assertEqual(
            res.data,
            {
                "name": self.user_details.name,
                "email": self.user_details.email,
            },
        )

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        # make a post request to the me url
        res = self.client.post(ME_URL, {})

        # assert that the response status code is 405 (method not allowed)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            "name": "Updated Name",
            "password": "newpassword123",
        }

        # make a patch request to the me url with the payload
        res = self.client.patch(ME_URL, payload)

        # refresh the user details from the db
        self.user_details.refresh_from_db()

        # assert that the user details were updated
        self.assertEqual(self.user_details.name, payload["name"])
        # assert that the password was updated
        self.assertTrue(self.user_details.check_password(payload["password"]))
        # assert that the response status code is 200 (success)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
