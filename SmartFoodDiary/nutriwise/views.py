from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import UserProfile

@login_required
def dashboard(request):
    """
    Render the main dashboard.
    The user must be logged in to access.
    """
    user_profile = UserProfile.objects.filter(user=request.user).first()
    context = {
        'user': request.user,
        'user_profile': user_profile,  # Pass profile data to the template
    }
    return render(request, 'nutriwise/dashboard.html', context)

@login_required
def dashboard2(request):
    """
    Render an alternative dashboard.
    The user must be logged in to access.
    """
    user_profile = UserProfile.objects.filter(user=request.user).first()
    context = {
        'user': request.user,
        'user_profile': user_profile,  # Pass profile data to the template
    }
    return render(request, 'nutriwise/dashboard2.html', context)

@login_required
def update_profile(request):
    """
    Update the user's profile information.
    """
    # Get or create the user's profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        try:
            # Update profile fields with data from the form
            user_profile.age = int(request.POST.get('age', 0))
            user_profile.gender = request.POST.get('gender', '').capitalize()
            user_profile.height = float(request.POST.get('height', 0.0))
            user_profile.weight = float(request.POST.get('weight', 0.0))
            user_profile.bmi = (
                user_profile.weight / ((user_profile.height / 100) ** 2)
                if user_profile.height > 0 else 0
            )  # Automatically calculate BMI

            # Save the updated profile
            user_profile.save()
            messages.success(request, "Profile updated successfully!")
        except ValueError:
            messages.error(request, "Invalid input. Please check your data.")

        # Redirect to the dashboard or profile view
        return redirect('nutriwise:dashboard2')

    # Render the profile update form
    context = {'user_profile': user_profile}
    return render(request, 'nutriwise/profile_update.html', context)

@login_required
def profile_view(request):
    """
    Display the user's profile information.
    """
    user_profile = UserProfile.objects.filter(user=request.user).first()

    return render(request, 'nutriwise/profile.html', {
        'user': request.user,
        'user_profile': user_profile,  # Pass profile data to the template
    })
