from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Custom login view
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
def register(request):
    """
    Handles the registration of a new user.
    - Checks for password match, existing username, and email.
    - Creates an inactive user and sends an activation email.
    """
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Check for password match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('users:register')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('users:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('users:register')

        # Create the user but leave it inactive until email confirmation
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = full_name
        user.is_active = False  # User will not be active until email is verified
        user.save()

        # Send activation email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = request.build_absolute_uri(reverse('users:activate', args=[uid, token]))

        email_subject = "Activate Your Account"
        email_body = f"""
Hi,

Thank you for registering on our website. Please click the link below to activate your account:

{activation_link}

If you did not register for an account, please ignore this email.
"""
        send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [email])

        # Show success message
        messages.success(request, "Account created! Please check your email to activate your account.")
        return redirect('users:login')  # Redirect to login page after registration

    return render(request, 'users/register.html')



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
