"""
Serializers for recipe API.
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects."""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects."""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ("id", "title", "time_minutes", "price", "link", "tags")
        read_only_fields = ["id"]

    def _getor_create_tags(self, tags, recipe):
        """Handling getting or creating tags as needed."""
        # get the authenticated user from the request object
        auth_user = self.context["request"].user
        # loop through the tags and create a new tag object for each one if it doesn't exist else get the existing tag object
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    # override the create function to handle the many to many relationship with tags
    def create(self, validated_data):
        """Create a new recipe."""
        # pop tags from validated_data and set it to an empty list if it doesn't exist
        tags = validated_data.pop("tags", [])
        # create the recipe object with the remaining validated_data
        recipe = Recipe.objects.create(**validated_data)
        # if tags is not None, get or create the tags
        self._getor_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""
        # pop tags from validated_data and set it to an empty list if it doesn't exist
        tags = validated_data.pop("tags", [])
        # if tags is not None, clear the tags from the instance and get or create the tags
        if tags is not None:
            instance.tags.clear()
            self._getor_create_tags(tags, instance)
        # loop through the validated_data and set the attributes on the instance
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail objects."""

    class Meta:
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ("description",)
