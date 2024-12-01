from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.http import JsonResponse
from django.urls import reverse_lazy
import re  # For regex validation


# Custom login view
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def form_invalid(self, form):
        """
        Override form_invalid to check if the user exists and add a custom message if needed.
        """
        username = form.cleaned_data.get('username', None)
        user = User.objects.filter(username=username).first()
        if not user:
            messages.error(self.request, "Please register.", extra_tags='register-error')
        else:
            messages.error(self.request, "Invalid username or password.", extra_tags='invalid-credentials')
        return super().form_invalid(form)


def home(request):
    return render(request, 'users/home.html')


# Registration view with validation
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        # Form is valid, but we need additional validation
        if form.is_valid():
            # Additional validation after form validation
            username = form.cleaned_data['username']
            phone_number = form.cleaned_data['phone_number']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            email = form.cleaned_data['email']

            # Validate username
            if len(username) < 8 or not re.search(r'[@/_]', username):
                form.add_error('username', "Username must be at least 8 characters long and include one of the following: @, /, or _.")
            
            # Validate phone number
            if len(phone_number) != 10 or not phone_number.isdigit():
                form.add_error('phone_number', "Phone number must contain exactly 10 digits.")
            
            # Validate passwords
            if password1 != password2:
                form.add_error('password2', "Passwords do not match.")
            elif len(password1) < 8:
                form.add_error('password1', "Password must be at least 8 characters long.")
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                form.add_error('email', "This email is already registered.")
            
            # If there are any form errors, return to the registration page with error messages
            if form.errors:
                print("Form errors:", form.errors)  # Print form errors to console
                messages.error(request, "Please correct the errors below.")
                return render(request, 'users/register.html', {'form': form})
            
            # Save the user but deactivate until email verification
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email verification
            user.save()

            # Ensure UserProfile is created or updated
            profile, created = UserProfile.objects.get_or_create(user=user)
            if not created:
                profile.full_name = form.cleaned_data.get('full_name')
                profile.phone_number = phone_number
                profile.save()

            # Send activation email with token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(reverse('users:activate', args=[uid, token]))

            email_subject = "Activate Your Account"
            email_body = f"""
            Hi {user.username},

            Thank you for registering on NUTRIWISE. Please click the link below to activate your account:

            {activation_link}

            If you did not register for an account, please ignore this email.
            """
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [user.email])

            messages.success(request, "Account created! Please check your email to activate your account.")
            return redirect('users:login')

        else:
            messages.error(request, "Please correct the errors below.")
            print("Form errors:", form.errors)  # Print form errors to console for debugging
            return render(request, 'users/register.html', {'form': form})

    else:
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})


# Account activation view
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated. You can now log in.")
        return redirect('users:login')
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return redirect('users:register')


# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Redirect to the 'next' URL or default
            next_url = request.GET.get('next', 'nutriwise:dashboard')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
def check_email(request):
    email = request.GET.get('email', None)
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})