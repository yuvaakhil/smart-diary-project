from django.shortcuts import render,redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm

class CustomLoginView(LoginView):
    template_name = 'users/login.html'  # Path to login form template


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')  # After registration, redirect to login
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


