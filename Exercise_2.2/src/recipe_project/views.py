from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # Django authentication libraries
from django.contrib.auth.forms import AuthenticationForm # Django Form for authentication
from django.utils.timezone import now, localtime
from .forms import SignupForm

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
  return render(request, 'auth/login.html', context)    # load the login page using "context" information

def logout_view(request):           # define a function-based view "logout_view" that takes a request from a user
  logout(request)                   # use the pre-defined Django function to logout the user
  return redirect('logout_success') # finds a named URL in urls.py and redirects there AFTER logout so timestamp persists

def logout_success(request):
  logout_time = localtime(now()).strftime('%m/%d/%Y @ %I:%M %p')
  return render(request, 'auth/logout_success.html', {'logout_time': logout_time}) # finds HTML file and renders it

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
  return render(request, 'auth/signup.html', context) # Render the signup page with the provided context