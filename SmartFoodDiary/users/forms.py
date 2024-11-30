from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone_number', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Ensure username is unique
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Ensure email is unique
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email should be unique and not already registered.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        # Skip all password validations like common passwords or numeric-only checks
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")
        # Skip all password validations
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user_profile = UserProfile(
            user=user,
            full_name=self.cleaned_data.get('full_name'),
            phone_number=self.cleaned_data.get('phone_number')
        )
        if commit:
            user.save()
            user_profile.save()
        return user