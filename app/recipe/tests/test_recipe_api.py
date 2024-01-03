"""
Test the recipe API
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def create_recipe(user, **params):
    """Helper function to create a recipe"""
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample description",
        "link": "https://sample.com/recipe",
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    # test that authentication is required to access the endpoint
    def test_auth_required(self):
        """Test that authentication is required"""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # test that authenticated user can retrieve recipes
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        # serializer converts model to json and vice versa, many=True for list of objects
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes only returns for authenticated user"""
        other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password="testpass123",
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        # filter recipes by user
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    # test that authenticated user can retrieve recipe detail
    def test_get_recipe_detail(self):
        """Test retrieving a recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    # test that authenticated user can create a recipe through the API
    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            "title": "Test recipe",
            "time_minutes": 10,
            "price": Decimal("5.00"),
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data["id"])
        # loop through payload and check if the values match the recipe object
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link=original_link,
        )

        payload = {"title": "New recipe title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link="https://exmaple.com/recipe.pdf",
            description="Sample recipe description.",
        )

        payload = {
            "title": "New recipe title",
            "link": "https://example.com/new-recipe.pdf",
            "description": "New recipe description",
            "time_minutes": 10,
            "price": Decimal("2.50"),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email="user2@example.com", password="test123")
        recipe = create_recipe(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email="user2@example.com", password="test123")
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            "title": "Test recipe",
            "time_minutes": 10,
            "price": Decimal("5.00"),
            "tags": [{"name": "Vegan"}, {"name": "Dessert"}],
        }
        response = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # get recipes of authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        # check if there is only one recipe
        self.assertEqual(recipes.count(), 1)
        # assign the first recipe to recipe variable
        recipe = recipes[0]
        # check if there are two tags assigned to the recipe we created
        self.assertEqual(recipe.tags.count(), 2)
        # loop through the tags and check if they exist in the database with the correct name and user
        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        """Test creating a recipe with existing tags."""
        tag_indian = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            "title": "Potato Curry",
            "time_minutes": 20,
            "price": Decimal("10.00"),
            "tags": [{"name": "Indian"}, {"name": "Breakfast"}],
        }
        response = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # get recipes of authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        # check if there is only one recipe
        self.assertEqual(recipes.count(), 1)
        # assign the first recipe to recipe variable
        recipe = recipes[0]
        # check if there are two tags assigned to the recipe we created
        self.assertEqual(recipe.tags.count(), 2)
        # check if the tag we created is in the tags of the recipe
        self.assertIn(tag_indian, recipe.tags.all())
        # loop through the tags and check if they exist in the database with the correct name and user
        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a tag when updating a recipe"""

        # create a sample recipe
        recipe = create_recipe(user=self.user)
        # create a payload with a new tag
        payload = {"tags": [{"name": "Lunch"}]}
        # create the url for the recipe detail
        url = detail_url(recipe.id)
        # http patch request to update the recipe with the new tag
        res = self.client.patch(url, payload, format="json")
        # check if the request was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # refresh the recipe from the database
        new_tag = Tag.objects.get(user=self.user, name="Lunch")
        # check if the new tag is in the recipe tags
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        # create a sample tag
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")
        # create a sample recipe
        recipe = create_recipe(user=self.user)
        # assign the tag to the recipe
        recipe.tags.add(tag_breakfast)

        # create a payload with a new tag
        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        payload = {"tags": [{"name": "Lunch"}]}
        url = detail_url(recipe.id)
        # http patch request to update the recipe with the new tag
        res = self.client.patch(url, payload, format="json")
        # check if the request was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # assert that the new tag is in the recipe tags
        self.assertIn(tag_lunch, recipe.tags.all())
        # assert that the first tag is not in the recipe tags
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing recipe tags"""
        # create a sample tag
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")
        # create a sample recipe
        recipe = create_recipe(user=self.user)
        # assign the tag to the recipe
        recipe.tags.add(tag_breakfast)

        # create a payload with a new tag
        payload = {"tags": []}
        url = detail_url(recipe.id)
        # http patch request to update the recipe with the new tag
        res = self.client.patch(url, payload, format="json")
        # check if the request was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # assert that the recipe has no tags
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        payload = {
            "title": "Test recipe",
            "time_minutes": 10,
            "price": Decimal("5.00"),
            "ingredients": [{"name": "Salt"}, {"name": "Pepper"}],
        }
        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # get recipes of authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        # check if there is only one recipe
        self.assertEqual(recipes.count(), 1)
        # assign the first recipe to recipe variable
        recipe = recipes[0]
        # check if there are two ingredients assigned to the recipe we created
        self.assertEqual(recipe.ingredients.count(), 2)
        # loop through the ingredients and check if they exist in the database with the correct name and user
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a recipe with existing ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name="Lemon")
        payload = {
            "title": "Lemonade",
            "time_minutes": 5,
            "price": Decimal("2.00"),
            "ingredients": [{"name": "Lemon"}, {"name": "Sugar"}],
        }
        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # get recipes of authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        # check if there is only one recipe
        self.assertEqual(recipes.count(), 1)
        # assign the first recipe to recipe variable
        recipe = recipes[0]
        # check if there are two ingredients assigned to the recipe we created
        self.assertEqual(recipe.ingredients.count(), 2)
        # check if the ingredient we created is in the ingredients of the recipe
        self.assertIn(ingredient, recipe.ingredients.all())
        # loop through the ingredients and check if they exist in the database with the correct name and user
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe"""

        # create a sample recipe
        recipe = create_recipe(user=self.user)
        # create a payload with a new ingredient
        payload = {"ingredients": [{"name": "Salt"}]}
        # create the url for the recipe detail
        url = detail_url(recipe.id)
        # http patch request to update the recipe with the new ingredient
        res = self.client.patch(url, payload, format="json")
        # check if the request was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # refresh the recipe from the database
        new_ingredient = Ingredient.objects.get(user=self.user, name="Salt")
        # check if the new ingredient is in the recipe ingredients
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe"""
        # create a sample ingredient
        ingredient_salt = Ingredient.objects.create(user=self.user, name="Salt")
        # create a sample recipe
        recipe = create_recipe(user=self.user)
        # assign the ingredient to the recipe
        recipe.ingredients.add(ingredient_salt)

        # create a payload with a new ingredient
        ingredient_pepper = Ingredient.objects.create(user=self.user, name="Pepper")
        payload = {"ingredients": [{"name": "Pepper"}]}
        url = detail_url(recipe.id)
        # http patch request to update the recipe with the new ingredient
        res = self.client.patch(url, payload, format="json")
        # check if the request was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # assert that the new ingredient is in the recipe ingredients
        self.assertIn(ingredient_pepper, recipe.ingredients.all())
        # assert that the first ingredient is not in the recipe ingredients
        self.assertNotIn(ingredient_salt, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing recipe ingredients"""
        # create a sample ingredient
        ingredient_salt = Ingredient.objects.create(user=self.user, name="Salt")
        # create a sample recipe
        recipe = create_recipe(user=self.user)
        # assign the ingredient to the recipe
        recipe.ingredients.add(ingredient_salt)

        # create a payload with a new ingredient
        payload = {"ingredients": []}
        url = detail_url(recipe.id)
        # http patch request to update the recipe with the new ingredient
        res = self.client.patch(url, payload, format="json")
        # check if the request was successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # assert that the recipe has no ingredients
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags"""
        r1 = create_recipe(user=self.user, title="Thai vegetable curry")
        r2 = create_recipe(user=self.user, title="Aubergine with tahini")
        tag1 = Tag.objects.create(user=self.user, name="Vegan")
        tag2 = Tag.objects.create(user=self.user, name="Vegetarian")
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title="Fish and chips")

        # filter recipes by tag1 and tag2
        params = {"tags": f"{tag1.id},{tag2.id}"}
        res = self.client.get(RECIPES_URL, params)

        # check if the response contains r1 and r2
        serializer1 = RecipeSerializer(r1)
        serializer2 = RecipeSerializer(r2)
        serializer3 = RecipeSerializer(r3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # check if the response does not contain r3
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients"""
        r1 = create_recipe(user=self.user, title="Posh beans on toast")
        r2 = create_recipe(user=self.user, title="Chicken cacciatore")
        i1 = Ingredient.objects.create(user=self.user, name="Feta cheese")
        i2 = Ingredient.objects.create(user=self.user, name="Chicken")
        r1.ingredients.add(i1)
        r2.ingredients.add(i2)
        r3 = create_recipe(user=self.user, title="Steak and mushrooms")

        # filter recipes by i1 and i2
        params = {"ingredients": f"{i1.id},{i2.id}"}
        res = self.client.get(RECIPES_URL, params)

        # check if the response contains r1 and r2
        serializer1 = RecipeSerializer(r1)
        serializer2 = RecipeSerializer(r2)
        serializer3 = RecipeSerializer(r3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # check if the response does not contain r3
        self.assertNotIn(serializer3.data, res.data)


class ImageUploadTests(TestCase):
    """Test for image upload API"""

    # runs before every test in this class
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="testpass123"
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    # runs after every test in this class
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        # create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            # go back to the beginning of the file because the save method moves the cursor to the end of the file
            image_file.seek(0)
            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        payload = {"image": "notanimage"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
