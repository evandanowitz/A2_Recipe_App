from django.test import TestCase
from .models import Recipe # to access Recipe model

# Create your tests here.
class RecipeModelTest(TestCase):
  def setUpTestData():
    # set up non-modified objects used by all test methods
    Recipe.objects.create(
      name = 'Turkey Sandwich',
      cooking_time = 3,
      ingredients = 'turkey, cheese, mayo, bread',
      difficulty = 'Easy',
      description = 'A simple sandwich with sliced turkey and cheese'
    )

  def test_recipe_name(self):
    # Get a recipe object to test
    recipe = Recipe.objects.get(id=1)
    # Compare the value to the expected result
    self.assertEqual(recipe.name, 'Turkey Sandwich')

  def test_name_max_length(self):
    recipe = Recipe.objects.get(id=1)
    max_length = recipe._meta.get_field('name').max_length
    self.assertEqual(max_length, 100)

  def test_ingredients_max_length(self):
    recipe = Recipe.objects.get(id=1)
    max_length = recipe._meta.get_field('ingredients').max_length
    self.assertEqual(max_length, 500)

  def test_difficulty_max_length(self):
    recipe = Recipe.objects.get(id=1)
    max_length = recipe._meta.get_field('difficulty').max_length
    self.assertEqual(max_length, 25)

  def test_cooking_time_help_text(self):
    recipe = Recipe.objects.get(id=1)
    help_text = recipe._meta.get_field('cooking_time').help_text
    self.assertEqual(help_text, 'in minutes')

  def test_ingredients_help_text(self):
    recipe = Recipe.objects.get(id=1)
    help_text = recipe._meta.get_field('ingredients').help_text
    self.assertEqual(help_text, 'Enter ingredients as a comma-separated list')

  def test_recipe_str(self):
    recipe = Recipe.objects.get(id = 1)
    self.assertEqual(str(recipe), recipe.name)