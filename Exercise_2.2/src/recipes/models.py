from django.db import models
from django.shortcuts import reverse

# Create your models here.

class Recipe(models.Model):
  name = models.CharField(max_length=100)
  cooking_time = models.IntegerField(help_text='in minutes')
  ingredients = models.TextField(
    max_length=500,
    help_text='Enter ingredients as a comma-separated list'
  )
  difficulty = models.CharField(max_length=25)
  description = models.TextField()

  def __str__(self):
    return str(self.name)
  
  def get_absolute_url(self):
    # refers to the primary key (ID) of that recipe in the database
    # the reverse() function generates the correct URL using this ID
    return reverse ('recipes:recipe_detail', kwargs={'pk': self.pk})
  
