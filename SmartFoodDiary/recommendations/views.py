from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from nutriwise.models import UserProfile, FoodDiaryEntry
from django.db.models import Sum
from .models import Notification
from datetime import  timedelta
from django.contrib import messages
from django.utils import timezone
from sklearn.neighbors import NearestNeighbors
import numpy as np
from nutriwise.models import UserProfile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import plotly.graph_objects as go
from django.db.models import Sum
import os
from io import BytesIO
from django.http import HttpResponse



now = timezone.now()
last_24_hours = now - timedelta(hours=24)


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


def check_and_notify(user_profile, request):
    """Check user profile for dietary conditions and send email notifications if necessary."""
    
    daily_entries = FoodDiaryEntry.objects.filter(user=user_profile.user, timestamp__gte=last_24_hours)

# Aggregate totals for the last 24 hours
    daily_totals = daily_entries.aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_fats=Sum('fats'),
        total_carbs=Sum('carbs'),
    )

    # Extract the values with default fallback to 0
    total_calories = daily_totals.get('total_calories', 0) or 0
    total_protein = daily_totals.get('total_protein', 0) or 0
    total_fats = daily_totals.get('total_fats', 0) or 0
    total_carbs = daily_totals.get('total_carbs', 0) or 0
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



def prepare_data_for_recommendation(user_profile, meal_features, meals):
    # Fetch the food entries for the user (still based on the user's food diary entries)
    food_entries = FoodDiaryEntry.objects.filter(user=user_profile.user)
    
    # Aggregate the user's food diary to get daily totals
    totals = food_entries.aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbs'),
        total_fats=Sum('fats'),
    )
    
    # Get the totals (default to 0 if no entries)
    user_features = [
        totals.get('total_calories', 0),
        totals.get('total_protein', 0),
        totals.get('total_carbs', 0),
        totals.get('total_fats', 0),
    ]
    
    return np.array(user_features).reshape(1, -1), np.array(meal_features), meals




def suggest_meals(user_profile, meal_features, meals):
    
    """Suggest meals based on user profile, recent food intake, and daily goals."""
    # Fetch food entries for the last 24 hours
    food_entries = FoodDiaryEntry.objects.filter(user=user_profile.user, timestamp__gte=last_24_hours)
    
    # Aggregate user's daily intake
    aggregated_data = food_entries.aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbs'),
        total_fats=Sum('fats'),
    )
    
    # Extract user totals
    user_totals = {
        'calories': aggregated_data.get('total_calories', 0) or 0,
        'protein': aggregated_data.get('total_protein', 0) or 0,
        'carbs': aggregated_data.get('total_carbs', 0) or 0,
        'fats': aggregated_data.get('total_fats', 0) or 0,
    }
    
    # Goals
    user_goals = {
        'calories': user_profile.calorie_goal,
        'protein': user_profile.protein_goal,
        'carbs': user_profile.carbs_goal,
        'fats': user_profile.fats_goal,
    }
    
    # Determine needs
    needs = {
        nutrient: user_goals[nutrient] - user_totals[nutrient]
        for nutrient in user_goals
    }
    
    # Prepare recommendations
    recommendations = []
    for i, meal in enumerate(meals):
        # Extract meal features
        meal_calories, meal_protein, meal_carbs, meal_fats = meal_features[i]
        
        # Filter meals based on needs
        if needs['calories'] < 0 and meal_calories < 300:
            # Recommend low-calorie meals
            recommendations.append((meals[i], meal_features[i]))
        elif needs['protein'] > 0 and meal_protein > 10:
            # Recommend protein-rich meals
            recommendations.append((meals[i], meal_features[i]))
        elif needs['carbs'] > 0 and meal_carbs > 15:
            # Recommend carb-rich meals
            recommendations.append((meals[i], meal_features[i]))
        elif needs['fats'] > 0 and meal_fats > 5:
            # Recommend fat-rich meals
            recommendations.append((meals[i], meal_features[i]))
    
    # Sort recommendations by priority (lowest calories or highest deficiency compensation)
    recommendations = sorted(
        recommendations,
        key=lambda x: (
            abs(needs['calories']) - x[1][0],  # Closest calorie match
            abs(needs['protein']) - x[1][1],  # Closest protein match
            abs(needs['carbs']) - x[1][2],    # Closest carb match
            abs(needs['fats']) - x[1][3],     # Closest fat match
        )
    )
    
    # Return the top recommendations
    return [meal[0] for meal in recommendations[:5]]  # Top 5 recommendations




@login_required
def meal_recommendations(request):
    try:
        # Get user profile
        profile = UserProfile.objects.get(user=request.user)
        
        # Get food entries and aggregated data
        food_entries = FoodDiaryEntry.objects.filter(user=request.user)
        aggregated_data = food_entries.aggregate(
            total_calories=Sum('calories'),
            total_protein=Sum('protein'),
            total_carbs=Sum('carbs'),
            total_fats=Sum('fats'),
        )

        # Calculate totals
        total_goals = (profile.calorie_goal + profile.protein_goal + 
                      profile.carbs_goal + profile.fats_goal)
        
        total_consumed = (
            (aggregated_data['total_calories'] or 0) +
            (aggregated_data['total_protein'] or 0) +
            (aggregated_data['total_carbs'] or 0) +
            (aggregated_data['total_fats'] or 0)
        )

        # Get meal recommendations using a relative path
        excel_file_path = "Anuvaad_INDB_2024.11.xlsx"

        try:
            meal_features, meals = load_meal_data_from_excel(excel_file_path)
            recommended_meals = suggest_meals(profile, meal_features, meals)
        except (PermissionError, FileNotFoundError) as e:
            # Handle file access errors gracefully
            recommended_meals = []
            messages.error(request, f"Could not access meal recommendations data: {str(e)}")

        context = {
            'user_profile': profile,
            'aggregated_data': aggregated_data,
            'recommended_meals': recommended_meals,
            'total_goals': total_goals,
            'total_consumed': total_consumed,
        }

        return render(request, 'recommendations/statistics.html', context)
    
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("User profile not found. Please complete your profile.")
    





import pandas as pd

def load_meal_data_from_excel(file_path):
    """Load meal data from Excel file with error handling."""
    try:
        # Load the Excel file
        df = pd.read_excel(file_path)

        # Ensure required columns exist
        required_columns = ['food_name', 'energy_kcal', 'protein_g', 'carb_g', 'fat_g']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # Extract meal features (numeric data only)
        numeric_columns = ['energy_kcal', 'protein_g', 'carb_g', 'fat_g']
        meal_features = df[numeric_columns].values

        # Extract meal names
        meals = df['food_name'].values

        return meal_features, meals

    except Exception as e:
        # Log the error (you should configure logging properly)
        print(f"Error loading meal data: {str(e)}")
        # Return empty data rather than raising an exception
        return np.array([]), np.array([])




@login_required
def generate_pdf_report(request):
    """
    Generate a PDF report with nutrient details.
    """
    # Get user profile
    profile = UserProfile.objects.get(user=request.user)
    
    # Fetch user data
    food_entries = FoodDiaryEntry.objects.filter(user=request.user).order_by('-timestamp')
    aggregated_data = FoodDiaryEntry.objects.filter(user=request.user).aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbs'),
        total_fats=Sum('fats'),
    )

    # Calculate totals
    total_goals = (profile.calorie_goal + profile.protein_goal + 
                  profile.carbs_goal + profile.fats_goal)
    
    total_consumed = (
        (aggregated_data['total_calories'] or 0) +
        (aggregated_data['total_protein'] or 0) +
        (aggregated_data['total_carbs'] or 0) +
        (aggregated_data['total_fats'] or 0)
    )

    # Prepare context
    context = {
        'user': request.user,
        'user_profile': profile,
        'food_entries': food_entries,
        'aggregated_data': aggregated_data,
        'total_goals': total_goals,
        'total_consumed': total_consumed,
    }

    # Render the PDF template
    template = get_template('recommendations/pdf_template.html')  # Use the new template
    html_content = template.render(context)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="nutrition_report.pdf"'
    
    # Create PDF with proper encoding and options
    pisa_status = pisa.CreatePDF(
        BytesIO(html_content.encode("UTF-8")),
        dest=response,
        encoding='utf-8',
        show_error_as_pdf=True
    )
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF <pre>' + html_content + '</pre>')

    return response


import csv

@login_required
def export_csv(request):
    """
    Export food and nutrient details to a CSV file.
    """
    # Fetch user data
    food_entries = FoodDiaryEntry.objects.filter(user=request.user).order_by('-timestamp')

    # Prepare response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="food_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Food Name', 'Calories', 'Carbs', 'Fats', 'Protein', 'Meal Logged Time'])

    for entry in food_entries:
        writer.writerow([
            entry.food_name,
            entry.calories,
            entry.carbs,
            entry.fats,
            entry.protein,
            entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response