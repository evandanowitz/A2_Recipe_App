from django.db import models
from django.shortcuts import reverse

# Create your models here.

class Recipe(models.Model):
  name = models.CharField(max_length=120)
  cooking_time = models.IntegerField(help_text='in minutes')
  ingredients = models.TextField(
    max_length = 500,
    help_text = 'Enter ingredients as a comma-separated list',
    blank=True # Allows empty submissions in forms
  )
  difficulty = models.CharField(max_length=25, editable=False)
  description = models.TextField()
  pic = models.ImageField(upload_to='recipes', default='no_picture.jpg')

  def __str__(self):
    return str(self.name)
  
  def get_absolute_url(self):
    # refers to the primary key (ID) of that recipe in the database
    # the reverse() function generates the correct URL using this ID
    return reverse ('recipes:recipe_detail', kwargs={'pk': self.pk})
  
  def return_ingredients_as_list(self):
    # converts ingredients string into a list
    if self.ingredients:
      return [ingredient.strip() for ingredient in self.ingredients.split(',')]
    return []

