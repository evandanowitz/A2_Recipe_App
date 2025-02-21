from django.shortcuts import render                           # imported by default
from .models import Recipe                                    # to access the Recipe model
from django.views.generic import ListView, DetailView         # to display lists and details
from django.contrib.auth.mixins import LoginRequiredMixin     # to protect class-based view
from django.contrib.auth.decorators import login_required     # to protect function-based view
from django.contrib import messages                           # import Django messages framework
from .forms import RecipeSearchForm                           # import RecipeSearchForm class
import pandas as pd                                           # import pandas. refer to it as 'pd'
from .utils import get_chart                                  # to call the get_chart() function

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
  form = RecipeSearchForm(request.GET or None) # Create an instance of RecipeSearchForm that was defined in recipes/forms.py. Allow GET requests for filtering
  qs_recipes = Recipe.objects.all() # Retrieve all recipes from the database (a QuerySet)
  recipes_df = None # Initialize pandas DataFrame as None
  chart = None # Initialize chart variable as None
  chart_error_msg = None # Initialize an error message variable

  # Get search input from the form
  recipe_name = request.GET.get('recipe_name', '').strip() # Get recipe name input from the search form
  ingredient = request.GET.get('ingredient', '').strip() # Get ingredient input from the search form
  difficulty = request.GET.get('difficulty', '') # Get difficulty level selection from the search form
  chart_type = request.GET.get('chart_type', '') # Get chart type selection from the search form

  # Apply filters based on user input (only if any filter is present)
  if recipe_name or ingredient or difficulty:
    if recipe_name:
      qs_recipes = qs_recipes.filter(name__icontains=recipe_name) # Partial match
    if ingredient:
      qs_recipes = qs_recipes.filter(ingredients__icontains=ingredient) # Partial match
    if difficulty:
      qs_recipes = qs_recipes.filter(difficulty=difficulty) # Exact match

  if qs_recipes.exists(): # Convert the QuerySet to a Pandas DataFrame (if there are matching recipes/results)
    recipes_df = pd.DataFrame(qs_recipes.values()) # Convert QuerySet to DataFrame
    recipes_df = recipes_df.to_html() # Convert DataFrame to HTML table

    if chart_type: # Generate chart if a chart type is selected
      chart = get_chart(chart_type, pd.DataFrame(qs_recipes.values()))
      if chart is None: # Check if get_chart() returned None
        chart_error_msg = 'Invalid chart type selected. Please choose a valid chart.'

