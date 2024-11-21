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
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


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





from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user but deactivate until email verification
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email verification
            user.save()

            # Ensure UserProfile is created or updated
            full_name = form.cleaned_data.get('full_name')
            phone_number = form.cleaned_data.get('phone_number')

            # Try to get the existing profile or create a new one if none exists
            profile, created = UserProfile.objects.get_or_create(user=user)
            if not created:
                # If the profile exists, update the information
                profile.full_name = full_name
                profile.phone_number = phone_number
                profile.save()

            # Send activation email with token
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

            messages.success(request, "Account created! Please check your email to activate your account.")
            return redirect('users:login')
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'users/register.html', {'form': form})

    else:
        form = CustomUserCreationForm()
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