from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from nutriwise.models import UserProfile, FoodDiaryEntry
from django.db.models import Sum
from .models import Notification

def create_notification(user, message):
    """Create a notification in the database."""
    Notification.objects.create(user=user, message=message)

def send_notification_email(user, message_subject, message_body):
    """Send email notification to the user."""
    send_mail(
        subject=message_subject,
        message=message_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

from django.contrib import messages

def check_and_notify(user_profile, request):
    """Check user profile for dietary conditions and send email notifications if necessary."""
    
    total_calories = FoodDiaryEntry.objects.filter(user=user_profile.user).aggregate(Sum('calories'))['calories__sum'] or 0
    total_protein = FoodDiaryEntry.objects.filter(user=user_profile.user).aggregate(Sum('protein'))['protein__sum'] or 0
    total_fats = FoodDiaryEntry.objects.filter(user=user_profile.user).aggregate(Sum('fats'))['fats__sum'] or 0
    total_carbs = FoodDiaryEntry.objects.filter(user=user_profile.user).aggregate(Sum('carbs'))['carbs__sum'] or 0

    # Check if goals are exceeded or unmet and send notifications
    if total_calories > user_profile.calorie_goal:
        subject = "Calorie Goal Exceeded"
        body = f"Dear {user_profile.user.username},\n\nYou have exceeded your daily calorie goal of {user_profile.calorie_goal:.2f} calories. You have consumed {total_calories:.2f} calories today.\n\nBest regards,\nNutriwise"
        send_notification_email(user_profile.user, subject, body)
        create_notification(user_profile.user, body)
        messages.success(request, "Calorie goal exceeded! An email has been sent to your inbox.")

    if total_protein < user_profile.protein_goal:
        subject = "Protein Goal Not Met"
        body = f"Dear {user_profile.user.username},\n\nYou have not met your daily protein goal of {user_profile.protein_goal:.2f} grams. You have consumed {total_protein:.2f} grams of protein today.\n\nBest regards,\nNutriwise"
        send_notification_email(user_profile.user, subject, body)
        create_notification(user_profile.user, body)
        messages.success(request, "Protein goal not met! An email has been sent to your inbox.")
    
    if total_fats > user_profile.fats_goal:
        subject = "Fat Goal Exceeded"
        body = f"Dear {user_profile.user.username},\n\nYou have exceeded your daily fat goal of {user_profile.fats_goal:.2f} grams. You have consumed {total_fats:.2f} grams of fats today.\n\nBest regards,\nNutriwise"
        send_notification_email(user_profile.user, subject, body)
        create_notification(user_profile.user, body)
        messages.success(request, "Fat goal exceeded! An email has been sent to your inbox.")
    
    if total_carbs < user_profile.carbs_goal:
        subject = "Carbohydrate Goal Not Met"
        body = f"Dear {user_profile.user.username},\n\nYou have not met your daily carbohydrate goal of {user_profile.carbs_goal:.2f} grams. You have consumed {total_carbs:.2f} grams of carbs today.\n\nBest regards,\nNutriwise"
        send_notification_email(user_profile.user, subject, body)
        create_notification(user_profile.user, body)
        messages.success(request, "Carbohydrate goal not met! An email has been sent to your inbox.")


def update_profile(request):
    # Get the user profile
    profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Update profile fields (e.g., calorie intake, protein intake, etc.)
        # Assuming that food entries are already being stored in the database
        check_and_notify(profile)  # Check and send notifications if needed
    
    return render(request, 'nutriwise/dashboard2.html', {'profile': profile})
