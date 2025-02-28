from django.shortcuts import render, redirect                 # imported render and redirect ( imported by default? )
from django.shortcuts import get_object_or_404                # import
from .models import Recipe                                    # to access the Recipe model
from django.views.generic import ListView, DetailView         # to display lists and details
from django.contrib.auth.mixins import LoginRequiredMixin     # to protect class-based view
from django.contrib.auth.decorators import login_required     # to protect function-based view
from django.contrib import messages                           # import Django messages framework
from .forms import RecipeSearchForm                           # import RecipeSearchForm class
import pandas as pd                                           # import pandas. refer to it as 'pd'
from .utils import get_chart                                  # to call the get_chart() function
from .forms import CreateRecipeForm

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

  # Pass recipes, form, and chart to the template (recipes_list.html file)
  return render(request, 'recipes/recipes_list.html', {
    'object_list': qs_recipes,            # Pass the filtered recipes 
    'form': form,                         # Pass the search form
    'recipes_df': recipes_df,             # Pass the DataFrame for table display
    'chart': chart,                       # Pass the generated chart
    'chart_error_msg': chart_error_msg    # Pass the chart error message 
  })

def create_recipe_view(request):
  error_message = None # Initialize error_message variable
  success_message = None # Initialize success_message variable
  recipe = None # Initialize recipe variable

  if request.method == 'POST':
    form = CreateRecipeForm(request.POST, request.FILES) # Include FILES for image uploads
    if form.is_valid():
      recipe = form.save() # Save the new recipe to the database
      success_message = "Recipe created successfully!"
      form = CreateRecipeForm() # Reset the form
    else:
      error_message = form.errors.as_ul() # Display form errors
  else:
    form = CreateRecipeForm() # Display an empty form

  context = {
    'form': form,
    'recipe': recipe,
    'error_message': error_message,
    'success_message': success_message,
  }
  return render(request, 'recipes/create_recipe.html', context)

def edit_recipe_view(request, pk): # Accepts the primary key (pk) of the recipe to edit
  error_message = None
  success_message = None
  recipe = get_object_or_404(Recipe, pk=pk) # Retrieve the recipe object from the database or return a 404 error if not found

  if request.method == 'POST': # If the form is submitted (In Django forms, updating existing data is done with POST requests, not PUT). PUT mainly used for APIs
    form = CreateRecipeForm(request.POST, request.FILES, instance=recipe) # Populate form with the submitted data
    if form.is_valid(): # Validate the form
      form.save() # Save the changes to the database
      success_message = f"'{recipe.name}' has been successfully updated!"
      return render(request, 'recipes/edit_recipe.html', {'success_message': success_message, 'recipe': recipe}) # Load the edit recipe form template (Once recipe is updated, user is sent back to view the recipe)
    else:
      error_message = form.errors.as_ul() # Display form errors
  else:
    form = CreateRecipeForm(instance=recipe) # Populate the form with the existing recipe data

  return render(request, 'recipes/edit_recipe.html', {
    'form': form, # Pass form object
    'recipe': recipe, # Pass recipe object
    'error_message': error_message, # Pass error_message object
    'success_message': success_message, # Pass success_message object
  })

