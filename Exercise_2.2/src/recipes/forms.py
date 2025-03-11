from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Recipe
from django.utils.safestring import mark_safe

class SignupForm(UserCreationForm):
  """
  Custom signup form extending Django's built-in UserCreationForm.
  Adds optional fields for email and first name.
  """

  username = forms.CharField(
    max_length=50,
    help_text="50 characters or fewer. Letters, digits, and @/./+/- only."
  )

  password1 = forms.CharField(
    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    label="Password",
    help_text=mark_safe(
      "Your password must contain at least 8 characters.<br>"
      "Your password must be alphanumeric."
    )
  )

  password2 = forms.CharField(
    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    label="Confirm password",
    help_text="Enter the same password again for verification."
  )

  email = forms.CharField(
    required=False,
    help_text="Optional. Provide your email address if you'd like."
  )

  first_name = forms.CharField(
    required=False,
    help_text="Optional. Provide your first name if you'd like."
  )

  class Meta:
    """
    Defines metadata for the SignupForm.
    Specifies the model and fields to include in the form.
    """
    model = User
    fields = ['username', 'password1', 'password2', 'email', 'first_name']

# Chart type choices for search form
CHART_CHOICES = (
  ('', 'Select Chart Type...'),
  ('#1', 'Bar Chart'), # User selects "Bar Chart", stored as "#1"
  ('#2', 'Pie Chart'),
  ('#3', 'Line Chart')
)

# Difficulty level choices for search form
DIFFICULTY_CHOICES = (
  ('', 'Select Difficulty...'),
  ('Easy', 'Easy'), # User selects "Easy", stored as "Easy"
  ('Medium', 'Medium'),
  ('Intermediate', 'Intermediate'),
  ('Hard', 'Hard')
)

class RecipeSearchForm(forms.Form):
  """
  Form for searching recipes based on name, ingredients, difficulty, and chart type.
  """
  recipe_name = forms.CharField(
    max_length=120,
    required=False,
    label='Recipe Name',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter a recipe name...'
    })
  )
  
  ingredient = forms.CharField(
    max_length=120,
    required=False,
    label='Ingredient',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter an ingredient...'
    })
  )
  
  difficulty = forms.ChoiceField(
    choices=DIFFICULTY_CHOICES,
    required=False,
    label='Difficulty Level',
    widget=forms.Select(attrs={
      'class': 'form-select'
    })
  )
  
  chart_type = forms.ChoiceField(
    choices=CHART_CHOICES,
    required=False,
    label='Chart Type',
    widget=forms.Select(attrs={
      'class': 'form-select'
    })
  )

class CreateRecipeForm(forms.ModelForm):
  """
  Form for creating and editing recipes.
  Linked to the Recipe model.
  Use forms.ModelForm when form is directly linked to a database model.
  """
  pic = forms.ImageField(required=False)
  
  class Meta:
    """
    Defines metadata for CreateRecipeForm.
    Specifies the model and fields to include in the form.
    Connects form to Recipe model.
    """
    model = Recipe
    fields = ['name', 'cooking_time', 'ingredients', 'description', 'pic']
  
  def __init__(self, *args, **kwargs):
    """
    Customizes form initialization.
    - Applies Bootstrap 'form-control' class to all fields.
    - Sets default row size for 'ingredients' and 'description' fields.
    """
    super(CreateRecipeForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
      field.widget.attrs.update({'class': 'form-control'})
    
    self.fields['ingredients'].widget.attrs.update({'rows': 3})
    self.fields['description'].widget.attrs.update({'rows': 3})