from django.urls import path
from .views import home, recipe_list, RecipeDetailView

app_name = 'recipes'

urlpatterns = [
  path('', home, name='home'), # the URL to list all recipes
  path('recipes/', recipe_list, name='recipe_list'),
  path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'), # <pk> param indicates the primary key of the object
]