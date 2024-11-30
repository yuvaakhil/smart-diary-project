# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """
    Render the main dashboard.
    The user must be logged in to access.
    """
    return render(request, 'nutriwise/dashboard.html', {'user': request.user})

@login_required
def dashboard2(request):
    """
    Render an alternative dashboard.
    The user must be logged in to access.
    """
    return render(request, 'nutriwise/dashboard2.html', {'user': request.user})