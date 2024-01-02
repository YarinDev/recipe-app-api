"""
Database models.
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    # get the file extension from the filename
    ext = os.path.splitext(filename)[1]
    # generate a random filename
    filename = f"{uuid.uuid4()}{ext}"
    # return the path
    return os.path.join("uploads/recipe/", filename)


class UserManager(BaseUserManager):
    """Manager for user profiles."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("Users must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # custom user manager for our user model (above) to work with django cli commands (createsuperuser) and django admin (user model)
    objects = UserManager()
    # set email as username field for our custom user model
    USERNAME_FIELD = "email"


class Recipe(models.Model):
    """Recipe object."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # many to many relationship with Tag model means that a recipe can have many tags and a tag can have many recipes
    tags = models.ManyToManyField("Tag")
    # many to many relationship with Ingredient model means that a recipe can have many ingredients and an ingredient can have many recipes
    ingredients = models.ManyToManyField("Ingredient")
    # optional image upload field
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        """Return string representation of recipe."""
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Return string representation of tag."""
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Return string representation of ingredient."""
        return self.name
