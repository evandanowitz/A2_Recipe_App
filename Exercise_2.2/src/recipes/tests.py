from django.test import TestCase
from django.shortcuts import reverse
from .models import Recipe
from django.contrib.auth.models import User # Import User model for authentication testsing (Django-included)
from .forms import RecipeSearchForm # Import the search form
from .utils import get_chart
import pandas as pd
import base64

# =================================
# Model Tests: Testing Recipe Model
# =================================

# Create your tests here.
class RecipeModelTest(TestCase):
  @classmethod
  def setUpTestData(cls): # runs ONCE for all tests
    # set up non-modified objects used by all test methods. This runs ONCE for all tests in this class.
    cls.recipe = Recipe.objects.create( # this will create an object and save it in the database
      name = 'Turkey Sandwich',
      cooking_time = 3,
      ingredients = 'turkey, cheese, mayo, bread',
      difficulty = 'Easy',
      description = 'A simple sandwich with sliced turkey and cheese'
    )

  def test_recipe_name(self):
    self.assertEqual(self.recipe.name, 'Turkey Sandwich')

  def test_name_max_length(self):
    max_length = self.recipe._meta.get_field('name').max_length
    self.assertEqual(max_length, 120)

  def test_ingredients_max_length(self):
    max_length = self.recipe._meta.get_field('ingredients').max_length
    self.assertEqual(max_length, 500)

  def test_difficulty_max_length(self):
    max_length = self.recipe._meta.get_field('difficulty').max_length
    self.assertEqual(max_length, 25)

  def test_cooking_time_help_text(self):
    help_text = self.recipe._meta.get_field('cooking_time').help_text
    self.assertEqual(help_text, 'in minutes')

  def test_ingredients_help_text(self):
    help_text = self.recipe._meta.get_field('ingredients').help_text
    self.assertEqual(help_text, 'Enter ingredients as a comma-separated list')

  def test_recipe_str(self):
    self.assertEqual(str(self.recipe), self.recipe.name)

  # check if get_absolute_url() returns the correct link for a recipe
  def test_get_absolute_url(self):
    expected_url = reverse('recipes:recipe_detail', args=[self.recipe.id])
    self.assertEqual(self.recipe.get_absolute_url(), expected_url)

  # check if the difficult level is correctly calculated based on cooking time and ingredients
  def test_calculate_difficulty(self):
    self.recipe.calculate_difficulty() # call the function
    self.assertEqual(self.recipe.difficulty, "Medium") # expected difficulty level

# ===================================
# View Tests: Testing Pages and Links
# ===================================

class RecipeViewTest(TestCase):
  @classmethod
  def setUpTestData(cls): # runs ONCE for all tests
    # Creates a test user
    cls.user = User.objects.create_user(
      username = 'testuser',
      password = 'testpassword'
    )
    # Creates a test recipe
    cls.recipe = Recipe.objects.create(
      name = 'Turkey Sandwich',
      cooking_time = 3,
      ingredients = 'turkey, cheese, mayo, bread',
      difficulty = 'Easy',
      description = 'A simple sandwich with sliced turkey and cheese'
    )

  def setUp(self):
    # Logs in test user before each test
    self.client.login(username = 'testuser', password = 'testpassword')

# ===============
# Page Load Tests
# ===============

  # check if the home page loads successfully
  def test_home_page_loads(self):
    response = self.client.get(reverse('recipes:home'))
    self.assertEqual(response.status_code, 200) # page should load OK

  # check if the recipes list page loads successfully
  def test_recipes_list_page_loads(self):
    response = self.client.get(reverse('recipes:recipe_list'))
    self.assertEqual(response.status_code, 200) # page should load OK

  # check if the individual recipe details page loads successfully
  def test_recipe_details_page_loads(self):
    recipe_url = self.recipe.get_absolute_url()
    response = self.client.get(recipe_url)
    self.assertEqual(response.status_code, 200) # page should load OK

  # check if accessing a non-existent recipe returns a 404 error
  def test_recipe_detail_404(self):
    response = self.client.get(reverse('recipes:recipe_detail', args=[9999])) # fake ID
    self.assertEqual(response.status_code, 404) # should return a 404 error

# ===================================
# Functional Tests (Links, Templates)
# ===================================

  # check if the 'Back to Recipes' button correctly links to the recipes list
  def test_back_to_recipes_button_link(self):
    response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.id]))
    self.assertContains(response, reverse('recipes:recipe_list')) # button should link correctly

  def test_recipe_list_view(self):
    response = self.client.get('/recipes/')
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'recipes/recipes_list.html')

# ========================================
# Form Tests (All form-related test cases)
# ========================================

class SearchFormTest(TestCase):

  # ensure that the search form accepts valid input and works properly
  def test_valid_form(self):
    form_data = {
      'recipe_name': 'Pasta',
      'ingredient': 'Tomato',
      'difficulty': 'Easy',
      'chart_type': '#1' # Bar Chart
    }
    form = RecipeSearchForm(data = form_data)
    self.assertTrue(form.is_valid())

  # ensure that invalid data is correctly rejected
  def test_invalid_recipe_name_too_long(self):
    long_name = 'A' * 121
    form_data = {'recipe_name': long_name}
    form = RecipeSearchForm(data=form_data)
    self.assertFalse(form.is_valid())
    self.assertIn('recipe_name', form.errors)

  # ensure that the form initializes without unexpected default values
  def test_default_values(self):
    form = RecipeSearchForm()
    self.assertEqual(form.fields['difficulty'].initial, None)
    self.assertEqual(form.fields['chart_type'].initial, None)

  # ensure that optional form input fields do not throw validation errors
  def test_optional_fields(self):
    form_data = {} # Empty form
    form = RecipeSearchForm(data=form_data)
    self.assertTrue(form.is_valid()) # Should be valid even when empty

