"""
Views for user API.
"""
from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    # serializer class is the class that we want to use to create the object
    serializer_class = UserSerializer
