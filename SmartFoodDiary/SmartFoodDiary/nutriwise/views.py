from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """
    Render the user dashboard. The user must be logged in to access.
    """
    return render(request, 'nutriwise/dashboard.html', {'user': request.user})

