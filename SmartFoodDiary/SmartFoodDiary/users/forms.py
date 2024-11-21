from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Use Django's default User model, or replace with your custom model if needed

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, help_text="Enter your full name.")
    phone_number = forms.CharField(max_length=15, required=True, help_text="Enter your phone number.")

    class Meta:
        model = User  # Replace with your custom user model if applicable
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']
