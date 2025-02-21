# This file will be to specify the search form fields

from django import forms

# Specify chart type choices as a tuple
CHART_CHOICES = (
  ('', 'Select Chart Type...'),
  ('#1', 'Bar Chart'), # When user selects "Bar Chart", it is stored as "#1"
  ('#2', 'Pie Chart'),
  ('#3', 'Line Chart')
)

# Specify difficulty level choices as a tuple
DIFFICULTY_CHOICES = (
  ('', 'Select Difficulty...'),
  ('Easy', 'Easy'), # When user selects "Easy", it is stored as "Easy"
  ('Medium', 'Medium'),
  ('Intermediate', 'Intermediate'),
  ('Hard', 'Hard')
)

# Define class-based Form imported from Django forms
class RecipeSearchForm(forms.Form):
  # Allows users to search by recipe name
  recipe_name = forms.CharField(
    max_length=120,
    required=False,
    label='Recipe Name',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter a recipe name...'
    })
  )
  # Allows users to search by ingredient
  ingredient = forms.CharField(
    max_length=120,
    required=False,
    label='Ingredient',
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter an ingredient...'
    })
  )
  # Dropdown menu to filter recipes by difficulty level
  difficulty = forms.ChoiceField(
    choices=DIFFICULTY_CHOICES,
    required=False,
    label='Difficulty Level',
    widget=forms.Select(attrs={
      'class': 'form-select'
    })
  )
  # Dropdown menu to select chart type for data visualization
  chart_type = forms.ChoiceField(
    choices=CHART_CHOICES,
    required=False,
    label='Chart Type',
    widget=forms.Select(attrs={
      'class': 'form-select'
    })
  )