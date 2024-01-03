"""
Views for recipe API.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma separated list of tagsIDs to filter",
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="Comma separated list of ingredients IDs to filter",
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database."""

    serializer_class = serializers.RecipeDetailSerializer
    # queryset represents the objects that available for the viewset
    queryset = Recipe.objects.all()
    # authentication_classes and permission_classes are used to restrict access to the viewset
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        # split the query params by comma
        return [int(str_id) for str_id in qs.split(",")]

    # get_queryset is a function that returns the queryset
    # this function is used to filter the queryset based on the request
    # e.g. return Recipe.objects.filter(user=self.request.user) to return only recipes that belong to the user
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # get the tags and ingredients query params
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        # if tags are provided, filter the queryset by tags
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        # if ingredients are provided, filter the queryset by ingredients
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        # return the filtered queryset ordered by id and distinct
        return queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return serializers.RecipeSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # perform_create is a function that is called when creating an object
    # this function is used to modify the object before it is saved
    # e.g. add the user to the object before saving
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        # get the recipe object
        recipe = self.get_object()
        # get the serializer for the recipe object
        serializer = self.get_serializer(recipe, data=request.data)
        # validate the serializer
        if serializer.is_valid():
            # save the image
            serializer.save()
            # return the serializer data
            return Response(serializer.data, status=status.HTTP_200_OK)
        # return the serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned_only",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Return only tags assigned to recipes",
            )
        ]
    )
)
class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewset for recipe attributes."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        # if assigned_only is provided, filter the queryset by assigned_only
        assigned_only = bool(int(self.request.query_params.get("assigned_only", 0)))
        # get the queryset
        queryset = self.queryset
        # if assigned_only is True, filter the queryset by recipe__isnull=False
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        # return the queryset ordered by name and distinct
        return queryset.filter(user=self.request.user).order_by("-name").distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
