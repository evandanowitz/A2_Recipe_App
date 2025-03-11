from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User

class Recipe(models.Model):
  """
  Model representing a recipe.

  Fields:
  - user: Links a recipe to a specific user (nullable for public recipes).
  - name: Name of the recipe.
  - cooking_time: Time required to prepare the recipe (in minutes).
  - ingredients: List of ingredients stored as a comma-separated string.
  - difficulty: Auto-calculated difficulty level based on cooking time and ingredients.
  - description: Detailed description of the recipe.
  - pic: Image representing the recipe.
  """
 
  user = models.ForeignKey(
    User, 
    on_delete=models.CASCADE, 
    null=True, 
    blank=True
  ) # Links each recipe to a user (allows public recipes when null)
  
  name = models.CharField(max_length=120)
  
  cooking_time = models.IntegerField(help_text='in minutes')
  
  ingredients = models.TextField(
    max_length = 500,
    help_text = 'Enter ingredients as a comma-separated list',
    blank=True
  )
  
  difficulty = models.CharField(
    max_length=25, 
    editable=False
  )

  description = models.TextField()

  pic = models.ImageField(
    upload_to='recipes', 
    default='no_picture.jpg'
  ) # Stores images in 'media/recipes/' with a default fallback image

  def __str__(self):
    """
    Returns the recipe name as its string representation.
    """
    return str(self.name)
  
  def get_absolute_url(self):
    """
    Returns the absolute URL for a recipe detail page.
    Refers to primary key (ID) of that recipe in database.
    reverse() function generates correct URL using this ID.
    """
    return reverse ('recipes:recipe_detail', kwargs={'pk': self.pk})
  
  def return_ingredients_as_list(self):
    """
    Converts the comma-separated ingredient string into a list.
    Returns an empty list if no ingredients are provided.
    """
    if self.ingredients:
      return [ingredient.strip() for ingredient in self.ingredients.split(',')]
    return []

  def calculate_difficulty(self):
    """
    Determines and assigns a difficulty level to the recipe based on cooking time and number of ingredients
    """
    num_ingredients = len(self.return_ingredients_as_list())
    
    if self.cooking_time < 10 and num_ingredients < 4:
      self.difficulty = 'Easy'
    elif self.cooking_time < 10 and num_ingredients >= 4:
      self.difficulty = 'Medium'
    elif self.cooking_time >= 10 and num_ingredients < 4:
      self.difficulty = 'Intermediate'
    else:
      self.difficulty = 'Hard'

  def save(self, *args, **kwargs):
    """
    Overrides the save method in models.py to ensure difficulty is calclulated before saving a Recipe object to database.
    """
    self.calculate_difficulty()
    super().save(*args, **kwargs)