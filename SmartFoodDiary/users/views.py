from django.shortcuts import render,redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

class CustomLoginView(LoginView):
    template_name = 'users/login.html'  # Path to login form template


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user data
            return redirect('login')  # Redirect to login after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


