from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, FoodDiaryEntry
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import pandas as pd
import plotly.graph_objs as go
from django.shortcuts import render
from django.http import JsonResponse
from recommendations.views import check_and_notify
from django.db.models import Sum
from recommendations.models import Notification
from django.contrib.auth import logout


# Load the Excel sheet data into a DataFrame
EXCEL_PATH = 'Anuvaad_INDB_2024.11.xlsx'
nutrition_df = pd.read_excel(EXCEL_PATH)
nutrition_df['food_name'] = nutrition_df['food_name'].str.lower()

# Initialize model and processor for food image classification
processor = AutoImageProcessor.from_pretrained("dima806/indian_food_image_detection")
model = AutoModelForImageClassification.from_pretrained("dima806/indian_food_image_detection")

@login_required
def dashboard(request):
    """
    Render the main dashboard.
    The user must be logged in to access.
    """
    # Get or create the user profile
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'calorie_goal': 2000,
            'protein_goal': 50.0,
            'carbs_goal': 300.0,
            'fats_goal': 70.0,
        }
    )
    
    uploaded_images = FoodDiaryEntry.objects.filter(user=request.user).order_by('-timestamp')[:3]
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'uploaded_images': uploaded_images,
        'notifications': notifications, 
        'calorie_goal': user_profile.calorie_goal,
        'protein_goal': user_profile.protein_goal,
        'carbs_goal': user_profile.carbs_goal,
        'fats_goal': user_profile.fats_goal, 
    }
    return render(request, 'nutriwise/dashboard.html', context)


@login_required
def dashboard2(request):
    """
    A separate dashboard view for specific use cases.
    """
    user_profile = UserProfile.objects.filter(user=request.user).first()
    context = {
        'user': request.user,
        'user_profile': user_profile,
    }
    return render(request, 'nutriwise/dashboard2.html', context)

@login_required
def pie_chart_data(request):
    """Return aggregated data for a Pie Chart."""
    aggregated_data = FoodDiaryEntry.objects.filter(user=request.user).aggregate(
        total_calories=Sum('calories'),
        total_carbs=Sum('carbs'),
        total_fats=Sum('fats'),
        total_fiber=Sum('fiber'),
        total_sugar=Sum('sugar'),
        total_protein=Sum('protein'),
        total_sodium=Sum('sodium'),
        total_potassium=Sum('potassium'),
        total_cholesterol=Sum('cholesterol'),
    )

    data = {
        "labels": ['Calories', 'Carbs', 'Fats', 'Fiber', 'Sugar', 'Protein', 'Sodium', 'Potassium', 'Cholesterol'],
        "values": [
            aggregated_data.get('total_calories', 0) or 0,
            aggregated_data.get('total_carbs', 0) or 0,
            aggregated_data.get('total_fats', 0) or 0,
            aggregated_data.get('total_fiber', 0) or 0,
            aggregated_data.get('total_sugar', 0) or 0,
            aggregated_data.get('total_protein', 0) or 0,
            aggregated_data.get('total_sodium', 0) or 0,
            aggregated_data.get('total_potassium', 0) or 0,
            aggregated_data.get('total_cholesterol', 0) or 0,
        ],
    }

    return JsonResponse(data)

@login_required
def bar_chart_data(request):
    """Return aggregated data for a Bar Chart."""
    return pie_chart_data(request)  # Same functionality as pie_chart_data

@login_required
def line_chart_data(request):
    """Return aggregated data for a Line Chart."""
    return pie_chart_data(request)  # Same functionality as pie_chart_data

@login_required
def donut_chart_data(request):
    """Return aggregated data for a Donut Chart."""
    return pie_chart_data(request)  # Same functionality as pie_chart_data

@login_required
def waterfall_chart_data(request):
    """Return aggregated data for a Waterfall Chart."""
    return pie_chart_data(request)  # Same functionality as pie_chart_data

@login_required
def analyze_food_image(request):
    """Handles food image upload and nutritional analysis."""
    food_details = {}
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        try:
            food_details = classify_and_get_nutrition(image_file)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, 'food_analysis/upload_image.html', {
        'food_details': food_details,
    })


@login_required
def upload_image(request):
    """Handles food image upload and logs the entry."""
    food_details = {}

    if request.method == 'POST' and request.FILES.get('food_image'):
        image_file = request.FILES['food_image']

        try:
            # Classify the image and get nutrition details
            food_details = classify_and_get_nutrition(image_file)

            # Validate the classification
            if not food_details or 'name' not in food_details:
                messages.error(request, "Failed to classify the food. Please try again.")
                return render(request, 'nutriwise/upload_image.html', {'food_details': food_details})

            # Save the food entry to the database
            entry = FoodDiaryEntry.objects.create(
                user=request.user,
                food_name=food_details.get('name', 'Unknown Food'),
                food_image=image_file,
                calories=float(food_details.get('calories', '0').replace(' kcal', '').strip()),
                carbs=float(food_details.get('carbs', '0').replace(' g', '').strip()),
                fats=float(food_details.get('fats', '0').replace(' g', '').strip()),
                fiber=float(food_details.get('fiber', '0').replace(' g', '').strip()),
                sugar=float(food_details.get('sugar', '0').replace(' g', '').strip()),
                protein=float(food_details.get('protein', '0').replace(' g', '').strip()),
                sodium=float(food_details.get('sodium', '0').replace(' mg', '').strip()),
                potassium=float(food_details.get('potassium', '0').replace(' mg', '').strip()),
                cholesterol=float(food_details.get('cholesterol', '0').replace(' mg', '').strip()),
            )

            # Check goals and notify the user
            user_profile = UserProfile.objects.get(user=request.user)
            check_and_notify(user_profile, request)

            messages.success(request, f"Food '{food_details['name']}' has been logged successfully!")
            return redirect('food_diary')  # Redirect to the food diary page

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'nutriwise/upload_image.html', {'food_details': food_details})

@login_required
def update_profile(request):
    """
    Update the user's profile information.
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        try:
            # Update the profile fields
            user_profile.age = int(request.POST.get('age', 0))
            user_profile.gender = request.POST.get('gender', '').capitalize()
            user_profile.height = float(request.POST.get('height', 0.0))
            user_profile.weight = float(request.POST.get('weight', 0.0))
            user_profile.calorie_goal = int(request.POST.get('calorie_goal', 0))
            user_profile.protein_goal = int(request.POST.get('protein_goal', 0))
            user_profile.carbs_goal = int(request.POST.get('carbs_goal', 0))
            user_profile.fats_goal = int(request.POST.get('fats_goal', 0))

            # Notification settings
            user_profile.enable_notifications = request.POST.get('enable_notifications') == 'on'
            user_profile.notify_on_exceed = request.POST.get('notify_on_exceed') == 'on'
            
            # Diet type and food restrictions
            user_profile.diet_type = request.POST.get('diet_type', 'None')
            user_profile.food_restrictions = request.POST.get('food_restrictions', '')

            # Automatically calculate BMI
            user_profile.bmi = (
                user_profile.weight / ((user_profile.height / 100) ** 2)
                if user_profile.height > 0 else 0
            )
            
            user_profile.save()
            messages.success(request, "Profile updated successfully!")
        except ValueError:
            messages.error(request, "Invalid input. Please check your data.")

        return redirect('nutriwise:dashboard2')

    context = {'profile': user_profile}
    return render(request, 'nutriwise/dashboard2.html', context)

def custom_logout(request):
    logout(request)  # Log the user out
    messages.success(request, "You have successfully logged out.")
    return redirect("http://127.0.0.1:8000/login/") 

@login_required
def profile(request):
    """
    Render and handle user profile updates.
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            user_profile.age = request.POST.get('age') or None
            user_profile.gender = request.POST.get('gender') or None
            user_profile.height = request.POST.get('height') or None
            user_profile.weight = request.POST.get('weight') or None
            user_profile.calorie_goal = request.POST.get("calorie_goal")
            user_profile.protein_goal = request.POST.get("protein_goal")
            user_profile.carbs_goal = request.POST.get("carbs_goal")
            user_profile.fats_goal = request.POST.get("fats_goal")
            user_profile.save()

            messages.success(request, "Profile updated successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        return redirect('nutriwise:profile')

    return render(request, 'nutriwise/dashboard2.html', {'profile': user_profile})


def classify_and_get_nutrition(image_file):
    """
    Handles image classification and retrieves nutritional data from the Excel sheet.
    """
    try:
        # Load and preprocess the image
        image = Image.open(image_file)
        inputs = processor(images=image, return_tensors="pt")

        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)

        # Get predicted class labels
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = predictions.argmax(dim=-1).item()
        confidence = predictions[0, predicted_class].item()

        # Get label mapping and predicted class
        id2label = model.config.id2label
        predicted_label = id2label[predicted_class]

        # Normalize and match the food name in the Excel data
        formatted_label = predicted_label.replace("_", " ").strip().lower()
        nutrition_df['normalized_food_name'] = nutrition_df['food_name'].str.strip().str.lower()

        matched_food = nutrition_df[nutrition_df['normalized_food_name'] == formatted_label]

        if matched_food.empty:
            return {
                'name': formatted_label,
                'confidence': f"{confidence:.2%}",
                'calories': 'N/A kcal',
                'carbs': 'N/A g',
                'fats': 'N/A g',
                'fiber': 'N/A g',
                'sugar': 'N/A g',
                'protein': 'N/A g',
                'sodium': 'N/A mg',
                'potassium': 'N/A mg',
                'cholesterol': 'N/A mg',
            }

        # Extract the first match
        nutrition_info = matched_food.iloc[0]

        return {
            'name': nutrition_info['food_name'],
            'confidence': f"{confidence * 100:.2f}%",  # Convert to percentage with 2 decimals
            'calories': f"{nutrition_info['energy_kcal']:.2f} kcal",
            'carbs': f"{nutrition_info['carb_g']:.2f} g",
            'fats': f"{nutrition_info['fat_g']:.2f} g",
            'fiber': f"{nutrition_info['fibre_g']:.2f} g",
            'sugar': f"{nutrition_info['freesugar_g']:.2f} g",
            'protein': f"{nutrition_info['protein_g']:.2f} g",
            'sodium': f"{nutrition_info['sodium_mg']:.2f} mg",
            'potassium': f"{nutrition_info['potassium_mg']:.2f} mg",
            'cholesterol': f"{nutrition_info['cholesterol_mg']:.2f} mg",
        }

    except Exception as e:
        raise ValueError("An error occurred while processing the image. Please try again.")