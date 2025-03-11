# Django Shortcuts (Common Utility Functions)
from django.shortcuts import render, redirect, get_object_or_404

# Django Class-Based Views (CBVs)
from django.views.generic import ListView, DetailView

# Authentication & Authorization
from django.contrib.auth.mixins import LoginRequiredMixin     # Protect CBVs
from django.contrib.auth.decorators import login_required     # Protect FBVs
from django.contrib.auth import authenticate, login, logout   # Django authentication libraries
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

# Forms & Models
from .models import Recipe
from .forms import RecipeSearchForm, SignupForm, CreateRecipeForm

# Utilities & Additional Libraries
import pandas as pd
from .utils import get_chart

# Django Utlities
from django.utils.timezone import now, localtime
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.contrib import messages     # Django Messages Framework

class RecipeListView(LoginRequiredMixin, ListView):
  """ Protected ListView that displays all recipes for logged-in users. """
  model = Recipe
  template_name = 'recipes/recipes_home.html'

class RecipeDetailView(LoginRequiredMixin, DetailView):
  """ Protected DetailView that displays a single recipe's details for logged-in users. """
  model = Recipe
  template_name = 'recipes/recipe_details.html'

  def get_object(self, queryset=None):
    """ Override get_object() to handle cases where a recipe no longer exists. Displays an error message and returns None if the recipe is deleted. """
    try:
      return super().get_object(queryset)
    except Recipe.DoesNotExist:
      messages.error(self.request, 'The recipe no longer exists. Redirecting...')
      return None
    
  def get(self, request, *args, **kwargs):
    """ Override get() to check if the recipe exists before rendering. If the recipe is missing, redirect to the recipes list page. """
    obj = self.get_object()
    if obj is None:
      return HttpResponseRedirect(reverse('recipes:recipe_list'))
    return super().get(request, *args, **kwargs)

def home(request):
  """ Render homepage for all users (publicly accessible). Displays landing page with an intro to BiteBase. """
  return render(request, 'recipes/recipes_home.html')

@login_required
def recipe_list(request):
  """ Display the list of recipes, apply search filters, and generate charts. """
  
  form = RecipeSearchForm(request.GET or None)
  
  # Retrieve and remove any stored message about a deleted recipe
  deleted_recipe_message = request.session.pop('deleted_recipe_message', None)

  # Determine which recipes to show: Superusers see all; regular users see only their own
  if request.user.is_superuser:
    qs_recipes = Recipe.objects.filter(Q(user=request.user) | Q(user__isnull=True))
  else:
    qs_recipes = Recipe.objects.filter(user=request.user)

  # If a non-superuser has no recipes, clone public recipes for them
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

    # Fetch updated list of user-specific recipes
    qs_recipes = Recipe.objects.filter(user=request.user)

  # Get user's display name (use full name if available, otherwise username)
  display_name = request.user.get_full_name() if request.user.get_full_name() else request.user.username

  recipes_df = None
  chart = None
  chart_error_msg = None

  # Retrieve user search inputs
  recipe_name = request.GET.get('recipe_name', '').strip()
  ingredient = request.GET.get('ingredient', '').strip()
  difficulty = request.GET.get('difficulty', '')
  chart_type = request.GET.get('chart_type', '')

  # Apply filters if any search criteria are provided
  if recipe_name or ingredient or difficulty:
    if recipe_name:
      qs_recipes = qs_recipes.filter(name__icontains=recipe_name)
    if ingredient:
      qs_recipes = qs_recipes.filter(ingredients__icontains=ingredient)
    if difficulty:
      qs_recipes = qs_recipes.filter(difficulty=difficulty)

  no_results_message = 'No recipes match your search criteria.' if not qs_recipes.exists() else None

  # Convert QuerySet to DataFrame and convert DataFrame to HTML table (if results exist)
  if qs_recipes.exists():
    recipes_df = pd.DataFrame(qs_recipes.values())
    recipes_df = recipes_df.to_html()

    if chart_type:
      chart = get_chart(chart_type, pd.DataFrame(qs_recipes.values()))
      if chart is None:
        chart_error_msg = 'Invalid chart type selected. Please choose a valid chart.'

  return render(request, 'recipes/recipes_list.html', {
    'object_list': qs_recipes, # 'object_list' is default naming and is really just 'qs_recipes'
    'form': form,
    'recipes_df': recipes_df,
    'chart': chart,
    'chart_error_msg': chart_error_msg,
    'deleted_recipe_message': deleted_recipe_message,
    'no_results_message': no_results_message,
    'display_name': display_name
  })

@login_required
def create_recipe_view(request):
  """ Allow users to create a new recipe. Superusers can create public recipes. """

  error_message = None
  success_message = None
  recipe = None

  if request.method == 'POST':
    # Include FILES for image uploads
    form = CreateRecipeForm(request.POST, request.FILES)
    
    if form.is_valid():
      # Save the new recipe but do not commit yet
      recipe = form.save(commit=False)
      
      # If superuser creates a recipe, set it as public (user=None)
      if request.user.is_superuser:
        # Public recipe (accessible for all users)
        recipe.user = None
      else:
        # Private recipe (owned by the specific user)
        recipe.user = request.user

      # Save finalized recipe
      recipe.save()
      success_message = f'"{recipe.name}" created successfully!'
      # Reset form after successful submission
      form = CreateRecipeForm()

    else:
      # Capture and display form validation errors
      error_message = form.errors.as_ul()

  else:
    # Display empty form for GET requests
    form = CreateRecipeForm()

  context = {
    'form': form,
    'recipe': recipe,
    'error_message': error_message,
    'success_message': success_message,
  }

  return render(request, 'recipes/create_recipe.html', context)

@login_required
def edit_recipe_view(request, pk):
  """ Allow users to edit an existing recipe. """

  # Retrieve recipe by primary key
  recipe = Recipe.objects.filter(pk=pk).first()

  if recipe is None:
    messages.error(request, 'The recipe no longer exists. Redirecting to recipes list.')
    return HttpResponseRedirect(reverse('recipes:recipe_list'))

  if request.method == 'POST':
    form = CreateRecipeForm(request.POST, request.FILES, instance=recipe)

    if form.is_valid():
      form.save()
      success_message = f'"{recipe.name}" has been successfully updated!'
      
      # Reload form after updating recipe, displaying success message
      return render(
        request, 
        'recipes/edit_recipe.html', 
        {'success_message': success_message, 'recipe': recipe}
      )
    
    else:
      error_message = form.errors.as_ul()

  else:
    # Pre-populate form with existing recipe data
    form = CreateRecipeForm(instance=recipe)

  return render(
    request, 
    'recipes/edit_recipe.html', {
      'form': form, 
      'recipe': recipe,
    },
  )

@login_required
def delete_recipe_view(request, pk):
  """ Handles recipe deletion, ensuring proper redirection and session message. """
  
  # Retrieve recipe object or return a 404 if not found
  recipe = get_object_or_404(Recipe, pk=pk)
  
  if request.method == 'POST':
    # Store name before deletion
    recipe_name = recipe.name
    # Delete recipe from database
    recipe.delete()

    # Store success message in session to persist across redirection
    request.session['deleted_recipe_message'] = f'Recipe "{recipe_name}" was successfully deleted.'

    # Handle AJAX request (if deletion was triggered via AJAX)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
      return JsonResponse({'redicrect_url': reverse('recipes:recipe_list')})
    
    return redirect('recipes:recipe_list')
  
  return redirect('recipes:recipe_list')

def login_view(request):
  """ Handles user authentication using Django's built-in AuthenticationForm. """

  error_message = None
  form = AuthenticationForm()

  # Process form submission when the user clicks "Login" button
  if request.method == 'POST':
    # Populate form with submitted data
    form = AuthenticationForm(data = request.POST)

    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      # Use Django 'authenticate' function to authenticate user
      user = authenticate(username = username, password = password)
      
      if user is not None:
        # if user is authenticated, use pre-defined Django function to log in
        login(request, user)
        return redirect('recipes:recipe_list')
      else:
        error_message = 'Oops... something went wrong!'

  context = {
    'form': form,
    'error_message': error_message,
  }

  return render(request, 'recipes/auth/login.html', context)

def logout_view(request):
  """ Logs out the user and redirects to the logout success page. """
  
  # Logs out current user with pre-defined Django function
  logout(request)
  
  return redirect('recipes:logout_success')

def logout_success(request):
  """ Displays the logout success page with the timestamp of logout. """
  
  # Format logout time
  logout_time = localtime(now()).strftime('%m/%d/%Y @ %I:%M %p')

  return render(request, 'recipes/auth/logout_success.html', {'logout_time': logout_time})

def signup_view(request):
  """ Handles user signup, form validation, and automatic login after successful signup. """

  error_message = None
  success_message = None
  form = SignupForm()

  # Check if request is a form submission (POST request)
  if request.method == 'POST':
    
    # Populate form with submitted user data
    form = SignupForm(request.POST)
    
    if form.is_valid():
      # Save the new user to the database
      user = form.save()
      # Automatically log in the user after signup
      login(request, user)
      success_message = 'User has been successfully created!'

      # Clone public recipes from the superuser to the newly created user
      superuser = User.objects.get(username='evandanowitz') # Retrieve the superuser account
      public_recipes = Recipe.objects.filter(user=superuser) # Get all public recipes
      
      for recipe in public_recipes:
        # Create a copy of each public recipe for the new user
        Recipe.objects.create(
          user=user,
          name=recipe.name,
          cooking_time=recipe.cooking_time,
          ingredients=recipe.ingredients,
          difficulty=recipe.difficulty,
          description=recipe.description,
          pic=recipe.pic,
        )

      # Reset form after successful signup
      form = SignupForm()

    else:
      # Display detailed error messages for invalid form submission
      error_message = form.errors.as_ul()

  context = {
    'form': form,
    'error_message': error_message,
    'success_message': success_message,
  }

  return render(request, 'recipes/auth/signup.html', context)

def about_me_view(request):
  """ Renders the About Me page. """
  
  return render(request, 'recipes/about_me.html')

@login_required
def profile_view(request):
  """ Renders the user profile page with relevant account details and a button for account deletion. """
  
  # Retrieve user's name
  display_name = request.user.get_full_name()

  # If name is empty or blank, default to username
  if not display_name.strip():
    display_name = request.user.username
  
  # Retrieve name or set default message if not provided
  name = request.user.get_full_name()
  if not name.strip():
    name = 'Name not created at signup'

  # Retrieve email or set default message if not provided
  email = request.user.email
  if not email:
    email = 'Email not created at signup'

  context = {
    'username': request.user.username,
    'display_name': display_name,
    'name': name,
    'email': email
  }

  return render(request, 'recipes/profile.html', context)

@login_required
def delete_account_view(request):
  """ Handles user account deletion and logs out the user. """

  if request.method == 'POST':
    # Retrieve the currently logged-in user
    user = request.user
    # Display success message before deleting account
    messages.success(request, 'Your account has been deleted successfully.')
    # Permanently delete user account
    user.delete()
    # Log out user after deletion
    logout(request)
    # Redirect user to home page
    return redirect('recipes:home')