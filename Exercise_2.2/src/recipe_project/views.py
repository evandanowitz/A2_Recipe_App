from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # Django authentication libraries
from django.contrib.auth.forms import AuthenticationForm # Django Form for authentication
from django.utils.timezone import now, localtime

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