from django.shortcuts import render, redirect, get_object_or_404                 # imported render and redirect ( imported by default? )
from .models import Recipe                                                       # to access the Recipe model
from django.views.generic import ListView, DetailView                            # to display lists and details
from django.contrib.auth.mixins import LoginRequiredMixin                        # to protect class-based view
from django.contrib.auth.decorators import login_required                        # to protect function-based view
from django.contrib.auth import authenticate, login, logout                      # Django authentication libraries
from django.contrib.auth.forms import AuthenticationForm                         # Django Form for authentication
from django.contrib import messages                                              # import Django messages framework
from django.contrib.auth.models import User
from .forms import RecipeSearchForm, SignupForm, CreateRecipeForm                # import RecipeSearchForm, SignupForm, and CreateRecipeForm classes
import pandas as pd                                                              # import pandas. refer to it as 'pd'
from .utils import get_chart                                                     # to call the get_chart() function
from django.utils.timezone import now, localtime
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse

class RecipeListView(LoginRequiredMixin, ListView):           # class-based "protected" view
  model = Recipe                                              # specify model
  template_name = 'recipes/recipes_home.html'                 # specify template

class RecipeDetailView(LoginRequiredMixin, DetailView):       # class-based "protected" view
  model = Recipe                                              # specify model
  template_name = 'recipes/recipe_details.html'               # specify template

  def get_object(self, queryset=None):
    try:
      return super().get_object(queryset)
    except Recipe.DoesNotExist:
      messages.error(self.request, "The recipe no longer exists. Redirecting...")
      return None
    
  def get(self, request, *args, **kwargs):
    obj = self.get_object()
    if obj is None:
      return HttpResponseRedirect(reverse('recipes:recipe_list')) # Redirect to list page
    return super().get(request, *args, **kwargs)

def home(request):
  return render(request, 'recipes/recipes_home.html')

@login_required
def recipe_list(request):
  form = RecipeSearchForm(request.GET or None) # Create an instance of RecipeSearchForm that was defined in recipes/forms.py. Allow GET requests for filtering
  deleted_recipe_message = request.session.pop('deleted_recipe_message', None)

  if request.user.is_superuser:
    qs_recipes = Recipe.objects.filter(Q(user=request.user) | Q(user__isnull=True))
  else:
    qs_recipes = Recipe.objects.filter(user=request.user)

  if not qs_recipes.exists() and not request.user.is_superuser:
    public_recipes = Recipe.objects.filter(user__isnull=True)
    
    for recipe in public_recipes:
      Recipe.objects.create(
        user=request.user,
        name=recipe.name,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        difficulty=recipe.difficulty,
        description=recipe.description,
        pic=recipe.pic,
      )

    # Get all superuser-created public recipes
    qs_recipes = Recipe.objects.filter(user=request.user)

  display_name = request.user.get_full_name() if request.user.get_full_name() else request.user.username

  recipes_df = None
  chart = None
  chart_error_msg = None

  # Get search input from the form
  recipe_name = request.GET.get('recipe_name', '').strip()
  ingredient = request.GET.get('ingredient', '').strip()
  difficulty = request.GET.get('difficulty', '')
  chart_type = request.GET.get('chart_type', '')

  # Apply filters based on user input (only if any filter is present)
  if recipe_name or ingredient or difficulty:
    if recipe_name:
      qs_recipes = qs_recipes.filter(name__icontains=recipe_name) # Partial match
    if ingredient:
      qs_recipes = qs_recipes.filter(ingredients__icontains=ingredient) # Partial match
    if difficulty:
      qs_recipes = qs_recipes.filter(difficulty=difficulty) # Exact match

  no_results_message = "No recipes match your search criteria." if not qs_recipes.exists() else None

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
    'chart_error_msg': chart_error_msg,   # Pass the chart error message
    'deleted_recipe_message': deleted_recipe_message,
    'no_results_message': no_results_message,
    'display_name': display_name
  })

@login_required
def create_recipe_view(request):
  error_message = None # Initialize error_message variable
  success_message = None # Initialize success_message variable
  recipe = None # Initialize recipe variable

  if request.method == 'POST':
    form = CreateRecipeForm(request.POST, request.FILES) # Include FILES for image uploads
    if form.is_valid():
      recipe = form.save(commit=False) # Save the new recipe to the database
      
      if request.user.is_superuser: # If superuser creates a recipe, set it as public (user=None)
        recipe.user = None # Public recipes for all users
      else:
        recipe.user = request.user # Private recipe for the specific user
      recipe.save()
      success_message = f"'{recipe.name}' created successfully!"
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

@login_required
def edit_recipe_view(request, pk):
  recipe = Recipe.objects.filter(pk=pk).first()

  if recipe is None:
    messages.error(request, "The recipe no longer exists. Redirecting to recipes list.")
    return HttpResponseRedirect(reverse('recipes:recipe_list'))

  if request.method == 'POST':
    form = CreateRecipeForm(request.POST, request.FILES, instance=recipe)
    if form.is_valid():
      form.save()
      success_message = f"'{recipe.name}' has been successfully updated!"
      return render(request, 'recipes/edit_recipe.html', {'success_message': success_message, 'recipe': recipe}) # Load the edit recipe form template (Once recipe is updated, user is sent back to view the recipe)
    else:
      error_message = form.errors.as_ul()
  else:
    form = CreateRecipeForm(instance=recipe) # Populate the form with the existing recipe data

  return render(request, 'recipes/edit_recipe.html', {
    'form': form, # Pass form object
    'recipe': recipe, # Pass recipe object
    'error_message': error_message, # Pass error_message object
    'success_message': success_message, # Pass success_message object
  })

@login_required
def delete_recipe_view(request, pk):
  recipe = get_object_or_404(Recipe, pk=pk) # Retrieve the recipe object from the database or return a 404 error if not found
  
  if request.method == 'POST':
    recipe_name = recipe.name # Store name before deleting
    recipe.delete() # Delete the recipe from the database

    # Use Django messages framework to pass success message
    messages.success(request, f"Recipe '{recipe_name}' was successfully deleted.")

    # Redirect to all recipes list
    return redirect('recipes:recipe_list')
  
  return redirect('recipes:recipe_list') # Redirect back if method is not POST

def login_view(request): # define a function-based view "login_view", which shows a Login form based on Django's authentication form
  error_message = None # initialize error_message to None
  form = AuthenticationForm() # form object with username and password fields

  # when the user hits "Login" button, a POST request will be generated
  if request.method == 'POST':
    form = AuthenticationForm(data = request.POST) # read the data sent by the form via POST request

    if form.is_valid():                                 # check if the form is valid
      username = form.cleaned_data.get('username')      # read username
      password = form.cleaned_data.get('password')      # read password
      user = authenticate(username = username, password = password) # use Django authenticate function to validate the user
      
      if user is not None:
        # if user is authenticated, use pre-defined Django function to login
        login(request, user)
        return redirect('recipes:recipe_list') # and send user to desired page
      else: # in case of error
        error_message = 'Oops... something went wrong!' # print error message

  # prepare data to send from view to template
  context = {
    'form': form, # send the form data
    'error_message': error_message, # and the error message
  }
  return render(request, 'recipes/auth/login.html', context)    # load the login page using "context" information

def logout_view(request):           # define a function-based view "logout_view" that takes a request from a user
  logout(request)                   # use the pre-defined Django function to logout the user
  return redirect('recipes:logout_success') # finds a named URL in urls.py and redirects there AFTER logout so timestamp persists

def logout_success(request):
  logout_time = localtime(now()).strftime('%m/%d/%Y @ %I:%M %p')
  return render(request, 'recipes/auth/logout_success.html', {'logout_time': logout_time}) # finds HTML file and renders it

# This function handles GET and POST requests, redirects user to login page after signup, and shows form errors if there are issues.
# Valid form: User is saved, logged in, redirected to login.html      # Invalid form: Error message appears, re-renders signup page
def signup_view(request):
  error_message = None # Initialize error_message variable
  success_message = None # Initialize success_message variable
  form = SignupForm() # Initialize form variable

  if request.method == 'POST': # Check if the request is a POST request, If it is, process the form
    form = SignupForm(request.POST) # Receives user input
    
    if form.is_valid(): # If the form is valid
      user = form.save() # Save the user to the database
      login(request, user) # Automatically log in the user
      success_message = "User has been successfully created!"
      form = SignupForm() # Reset the form after successful signup

    else: # If form is invalid, display actual errors
      error_message = form.errors.as_ul() # Display detailed error messages

  context = { # Prepare context dictionary to pass data to the template
    'form': form, # The signup form instance (either empty or filled with user input)
    'error_message': error_message, # Error message to display if form validation fails
    'success_message': success_message, # Pass success message to template
  }
  return render(request, 'recipes/auth/signup.html', context) # Render the signup page with the provided context