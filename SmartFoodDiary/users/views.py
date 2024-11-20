from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm  # Import the custom user form once
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User

# Custom login view
class CustomLoginView(LoginView):
    template_name = 'users/login.html'


def home(request):
    return render(request, 'users/home.html')


def register(request):
    """
    Handles the registration of a new user.
    - Checks for password match, existing username, and email.
    - Creates an inactive user and sends an activation email.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user and additional profile fields (full_name, phone_number)
            user = form.save(commit=False)
            user.is_active = False  # User will not be active until email is verified
            user.save()

            # Send activation email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(reverse('users:activate', args=[uid, token]))

            email_subject = "Activate Your Account"
            email_body = f"""
            Hi,

            Thank you for registering on NUTRIWISE. Please click the link below to activate your account:

            {activation_link}

            If you did not register for an account, please ignore this email.
            """
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [user.email])

            # Show success message
            messages.success(request, "Account created! Please check your email to activate your account.")
            return redirect('users:login')  # Redirect to login page after registration
        else:
            # If form is invalid, display errors
            print(form.errors)
            messages.error(request, "ensure password length is 8.")
            return render(request, 'users/register.html', {'form': form})

    else:
        form = CustomUserCreationForm()  # Instantiate the form for GET request

    return render(request, 'users/register.html', {'form': form})


def activate_account(request, uidb64, token):
    """
    Activates a user account after clicking on the activation link.
    - Decodes the user ID and token, checks if valid, and activates the user.
    """
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


def activate(request, uidb64, token):
    """
    This function is an alternative for handling the activation link after the user clicks.
    It's also an activation endpoint if the first one doesn't work.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect('users:login')
    else:
        messages.error(request, "The activation link is invalid or expired.")
        return redirect('users:register')
