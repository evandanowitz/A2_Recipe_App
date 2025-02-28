from django.urls import path
from .views import home, recipe_list, RecipeDetailView, create_recipe_view, edit_recipe_view

app_name = 'recipes'

urlpatterns = [
  path('', home, name='home'), # the URL to list all recipes
  path('recipes/', recipe_list, name='recipe_list'),
  path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'), # <pk> param indicates the primary key of the object
  path('create-recipe/', create_recipe_view, name='create_recipe'), # DOES NOT require an existing recipe ID ( no <pk> )
  path('recipes/<int:pk>/edit/', edit_recipe_view, name='edit_recipe'), # Requires an existing recipe ID ( <pk> )
]