from django.shortcuts import render

# Create your views here.

# This function takes the request coming from the web application and, 
# returns the template available at recipes/home.html as a response
def home(request):
  return render(request, 'recipes/recipes_home.html')