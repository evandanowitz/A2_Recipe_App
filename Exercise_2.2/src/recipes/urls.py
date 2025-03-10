from django.conf import settings # Allows access to MEDIA_URL and MEDIA_ROOT variables
from django.conf.urls.static import static # Helper function for serving media files during development
from django.urls import path
from .views import (
  home, recipe_list, RecipeDetailView, create_recipe_view, edit_recipe_view, delete_recipe_view, 
  about_me_view, profile_view, delete_account_view, login_view, logout_view, logout_success, signup_view
)

app_name = 'recipes'

urlpatterns = [
  path('', home, name='home'), # the URL to list all recipes
  path('recipes/', recipe_list, name='recipe_list'),
  path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'), # <pk> param indicates the primary key of the object
  path('create-recipe/', create_recipe_view, name='create_recipe'), # DOES NOT require an existing recipe ID ( no <pk> )
  path('recipes/<int:pk>/edit/', edit_recipe_view, name='edit_recipe'), # Requires an existing recipe ID ( <pk> )
  path('recipes/<int:pk>/delete/', delete_recipe_view, name='delete_recipe'), # Requires an existing recipe ID ( <pk> ). The delete button in edit_recipe.html now links to this view
  path('about-me/', about_me_view, name='about_me'),
  path('profile/', profile_view, name='profile'),
  path('delete-account/', delete_account_view, name='delete_account'),

  # Authentication Routes
  path('login/', login_view, name='login'), # good practice to give names to your url and view mapping
  path('logout/', logout_view, name='logout'),
  path('logout-success/', logout_success, name='logout_success'),
  path('signup/', signup_view, name='signup'), # Allows users to access the signup page by visiting http...url.../signup/  
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)