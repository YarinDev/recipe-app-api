"""
Views for user API.
"""
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    # serializer class is the class that we want to use to create the object
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    # serializer class is the class that we want to use to create the object
    serializer_class = AuthTokenSerializer
    # renderer classes allows us to view the endpoint in the browser
    # we want to see the endpoint in the browser so we can test it
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
