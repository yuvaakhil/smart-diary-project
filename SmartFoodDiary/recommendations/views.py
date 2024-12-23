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
from django.shortcuts import render
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
    # Prepare data for model
    user_features, _, _ = prepare_data_for_recommendation(user_profile, meal_features, meals)
    
    # Ensure there are enough meals to train the model
    n_neighbors = min(5, len(meal_features))  # Use a maximum of 5 neighbors or the number of meals
    
    # Train a KNN model
    knn = NearestNeighbors(n_neighbors=n_neighbors)
    knn.fit(meal_features)
    
    # Find the closest meals based on the user's current intake
    distances, indices = knn.kneighbors(user_features)
    
    # Convert indices to integers before using them for list indexing
    indices = indices.flatten()  # Flatten the array
    indices = [int(i) for i in indices]  # Convert numpy int64 to Python int
    
    # Get recommended meals
    recommended_meals = [meals[i] for i in indices]
    
    return recommended_meals



@login_required
def meal_recommendations(request):
    recommended_meals = [] 
    try:
        # Load meal data from the Excel file
        meal_features, meals = load_meal_data_from_excel("C:\\Users\\yuvaa\\Desktop\\smart diary\\SmartFoodDiary\\Anuvaad_INDB_2024.11.xlsx")
        
        # Ensure the user is authenticated and has a profile
        if request.user.is_authenticated:
            # Get the user's profile
            profile = UserProfile.objects.get(user=request.user)
            
            # Get recommended meals using the KNN-based system
            recommended_meals = suggest_meals(profile, meal_features, meals)
            

            return render(request, 'recommendations/statistics.html', {'recommended_meals': recommended_meals})
        else:
            return HttpResponseForbidden("You need to log in to access this page.")
    
    except UserProfile.DoesNotExist:
        # Handle the case where the user does not have a profile
        return HttpResponseForbidden("User profile not found. Please complete your profile.")
    





import pandas as pd

def load_meal_data_from_excel(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path)

   

    # Assuming the necessary columns are present like 'food_name', 'energy_kcal', 'protein_g', 'carb_g', 'fat_g'
    # Extract only the numeric columns for the model
    numeric_columns = ['energy_kcal', 'protein_g', 'carb_g', 'fat_g']
    
    # Check if all the required numeric columns are present
    for col in numeric_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Extract meal features (numeric data only)
    meal_features = df[numeric_columns].values

    # Extract meal names (strings) for reference, but do not include them in the model
    meals = df['food_name'].values

    return meal_features, meals


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

@login_required
def generate_pdf_report(request):
    """
    Generate a PDF report with nutrient details without charts.
    """
    # Fetch user data
    food_entries = FoodDiaryEntry.objects.filter(user=request.user).order_by('-timestamp')
    aggregated_data = FoodDiaryEntry.objects.filter(user=request.user).aggregate(
        total_calories=Sum('calories'),
        total_carbs=Sum('carbs'),
        total_fats=Sum('fats'),
        total_fiber=Sum('fiber'),
        total_sugar=Sum('sugar'),
        total_protein=Sum('protein'),
    )
   

    # Render the PDF template
    template = get_template('recommendations/statistics.html')
    html_content = template.render({
    'user': request.user,
    'food_entries': food_entries,
    'aggregated_data': aggregated_data,
})

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="nutrition_report.pdf"'
    pisa_status = pisa.CreatePDF(BytesIO(html_content.encode("UTF-8")), dest=response)
    
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
