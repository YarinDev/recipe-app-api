"""
Views for recipe API.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database."""

    serializer_class = serializers.RecipeDetailSerializer
    # queryset represents the objects that available for the viewset
    queryset = Recipe.objects.all()
    # authentication_classes and permission_classes are used to restrict access to the viewset
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # get_queryset is a function that returns the queryset
    # this function is used to filter the queryset based on the request
    # e.g. return Recipe.objects.filter(user=self.request.user) to return only recipes that belong to the user
    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return serializers.RecipeSerializer

        return self.serializer_class

    # perform_create is a function that is called when creating an object
    # this function is used to modify the object before it is saved
    # e.g. add the user to the object before saving
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Manage tags in the database."""

    # mixins.ListModelMixin is used to list objects
    # viewsets.GenericViewSet is used to create a viewset without a model

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by("-name")
