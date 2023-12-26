"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    # Meta class is used to configure the serializer
    class Meta:
        model = get_user_model()
        # fields that will be converted to and from JSON when we make HTTP POST requests
        fields = ("email", "password", "name")
        # extra_kwargs allows us to configure a few extra settings in our model serializer
        # we want to make sure that the password field is write only, so it can only be used to create or update an object
        # we also want to make sure that the password is at least 5 characters long
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
