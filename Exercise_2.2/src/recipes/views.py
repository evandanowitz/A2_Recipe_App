from django.shortcuts import render                     # imported by default
from .models import Recipe                              # to access the Recipe model
from django.views.generic import ListView, DetailView   # to display lists and details

# Create your views here.

class RecipeListView(ListView):                   # class-based view
  model = Recipe                                  # specify model
  template_name = 'recipes/recipes_home.html'     # specify template

class RecipeDetailView(DetailView):               # class-based view
  model = Recipe                                  # specify model
  template_name = 'recipes/recipe_details.html'   # specify template

# This function takes the request coming from the web application and, 
# returns the template available at recipes/home.html as a response
def home(request):
  return render(request, 'recipes/recipes_home.html')