"""
URL mapping for recipe app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views

# router is used to register viewsets
# default router automatically generates the URL for the viewset
router = DefaultRouter()
router.register("recipes", views.RecipeViewSet)
router.register("tags", views.TagViewSet)

app_name = "recipe"

urlpatterns = [
    path("", include(router.urls)),
]
