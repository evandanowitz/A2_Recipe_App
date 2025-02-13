from django.shortcuts import render                           # imported by default
from .models import Recipe                                    # to access the Recipe model
from django.views.generic import ListView, DetailView         # to display lists and details
from django.contrib.auth.mixins import LoginRequiredMixin     # to protect class-based view
from django.contrib.auth.decorators import login_required     # to protect function-based view

# Create your views here.

class RecipeListView(LoginRequiredMixin, ListView):           # class-based "protected" view
  model = Recipe                                              # specify model
  template_name = 'recipes/recipes_home.html'                 # specify template

class RecipeDetailView(LoginRequiredMixin, DetailView):       # class-based "protected" view
  model = Recipe                                              # specify model
  template_name = 'recipes/recipe_details.html'               # specify template

# This function takes the request coming from the web application and, 
# returns the template available at recipes/home.html as a response
def home(request):
  return render(request, 'recipes/recipes_home.html')

@login_required # protected
def recipe_list(request):
  # retrieve all recipes from the database
  recipes = Recipe.objects.all()
  # pass all the recipes fetched to recipes_list.html file
  return render(request, 'recipes/recipes_list.html', {'object_list': recipes})