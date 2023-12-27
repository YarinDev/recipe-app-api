"""
Views for user API.
"""
from rest_framework import generics, authentication, permissions
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


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    # serializer class is the class that we want to use to create the object
    serializer_class = UserSerializer
    # authentication classes is the classes that we want to use to authenticate the user
    authentication_classes = (authentication.TokenAuthentication,)
    # permission classes is the classes that we want to use to authenticate the user has the correct permissions
    permission_classes = (permissions.IsAuthenticated,)

    # get_object is a function that is called when we want to get the object that the view is using
    def get_object(self):
        """Retrieve and return authenticated user"""
        # self.request is the request object that was made to the view
        # user is the user object that is attached to the request
        return self.request.user
