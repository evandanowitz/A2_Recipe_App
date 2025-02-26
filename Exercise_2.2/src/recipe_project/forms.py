from django import forms
from django.contrib.auth.forms import UserCreationForm # UserCreationForm is built-in with Django (includes username, password, and email validation).
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class SignupForm(UserCreationForm):
  
  username = forms.CharField(
    # widget=forms.TextInput(attrs={'placeholder': 'Enter your username ...'}),
    max_length=50,
    help_text="50 characters or fewer. Letters, digits, and @/./+/- only."
  )

  password1 = forms.CharField(
    # widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password ...'}),
    label="Password",
    help_text=mark_safe("Your password must contain at least 8 characters.<br>Your password must be alphanumeric.")
  )

  password2 = forms.CharField(
    # widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password ...'}),
    label="Confirm password",
    help_text="Enter the same password again for verification."
  )

  email = forms.CharField(
    # widget=forms.TextInput(attrs={'placeholder': 'Enter your email address ...'}),
    required=False,
    help_text="Optional. Provide your email address if you'd like."
  )

  first_name = forms.CharField(
    # widget=forms.TextInput(attrs={'placeholder': 'Enter your first name ...'}),
    required=False,
    help_text="Optional. Provide your first name if you'd like."
  )

  # Define 'Meta' class to specify which fields to include in Signup form
  class Meta:
    model = User
    fields = ['username', 'password1', 'password2', 'email', 'first_name']