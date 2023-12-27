"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from django.utils.translation import gettext as _

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

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # pop the password from the validated data (returns the value of the password and removes it from the dictionary)
        password = validated_data.pop("password", None)
        # call the update method on the instance
        user = super().update(instance, validated_data)

        # if the password exists, set the password securely using the set_password method instead of just setting the password attribute on the user object
        if password:
            user.set_password(password)
            # save the user object
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token"""

    email = serializers.EmailField()
    # trim_whitespace=False allows us to authenticate with an email that has trailing whitespace
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    # validate is a function that is called when we validate the serializer
    # attrs is the data that is passed into the serializer
    def validate(self, attrs):
        """Validate and authenticate the user"""
        # attrs is a dictionary of all the fields that make up our serializer
        email = attrs.get("email")
        password = attrs.get("password")

        # authenticate with the email and password
        user = authenticate(
            # context is the context of the request that was made
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        # if authentication fails, raise an authentication error
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authorization")

        # set the user attribute on the serializer to the user that was authenticated
        attrs["user"] = user
        # return the validated attributes
        return attrs
