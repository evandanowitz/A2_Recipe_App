from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
  home, recipe_list, RecipeDetailView, create_recipe_view, edit_recipe_view, delete_recipe_view, 
  about_me_view, profile_view, delete_account_view, login_view, logout_view, logout_success, signup_view
)

app_name = 'recipes'

urlpatterns = [
  path('', home, name='home'),
  path('recipes/', recipe_list, name='recipe_list'),
  path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
  path('create-recipe/', create_recipe_view, name='create_recipe'),
  path('recipes/<int:pk>/edit/', edit_recipe_view, name='edit_recipe'),
  path('recipes/<int:pk>/delete/', delete_recipe_view, name='delete_recipe'),
  path('about-me/', about_me_view, name='about_me'),
  path('profile/', profile_view, name='profile'),
  path('delete-account/', delete_account_view, name='delete_account'),

  path('login/', login_view, name='login'),
  path('logout/', logout_view, name='logout'),
  path('logout-success/', logout_success, name='logout_success'),
  path('signup/', signup_view, name='signup'),
]

# Serve media files during development mode
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)