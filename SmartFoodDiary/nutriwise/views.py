#views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, FoodDiaryEntry
from .forms import FoodDiaryEntryForm
from .forms import UserProfileForm
from PIL import Image
from django.http import JsonResponse
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import pandas as pd


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
    user_profile = UserProfile.objects.filter(user=request.user).first()
    uploaded_images = FoodDiaryEntry.objects.filter(user=request.user)
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'uploaded_images': uploaded_images,  
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
    return render(request, 'nutriwise/dashboard2.html', {'user': request.user})

@login_required
def pie_chart_data(request):
    """Fetch data for Pie Chart (e.g., nutrition breakdown for the uploaded food)."""
    # Get the most recent FoodDiaryEntry for the logged-in user
    latest_entry = FoodDiaryEntry.objects.filter(user=request.user).last()
    
    if latest_entry:
        # Use the nutrition information for the uploaded food
        labels = ['Calories', 'Carbs', 'Fats', 'Fiber', 'Sugar', 'Protein', 'Sodium', 'Potassium', 'Cholesterol']
        values = [
            latest_entry.calories,
            latest_entry.carbs,
            latest_entry.fats,
            latest_entry.fiber,
            latest_entry.sugar,
            latest_entry.protein,
            latest_entry.sodium,
            latest_entry.potassium,
            latest_entry.cholesterol
        ]
    else:
        labels = []
        values = []
    
    return JsonResponse({'labels': labels, 'values': values})



@login_required
def bar_chart_data(request):
    """Fetch data for Bar Chart (e.g., protein content of the uploaded food)."""
    latest_entry = FoodDiaryEntry.objects.filter(user=request.user).last()
    if latest_entry:
        # Use the nutrition information for the uploaded food
        labels = ['Calories', 'Carbs', 'Fats', 'Fiber', 'Sugar', 'Protein', 'Sodium', 'Potassium', 'Cholesterol']
        values = [
            latest_entry.calories,
            latest_entry.carbs,
            latest_entry.fats,
            latest_entry.fiber,
            latest_entry.sugar,
            latest_entry.protein,
            latest_entry.sodium,
            latest_entry.potassium,
            latest_entry.cholesterol
        ]
    else:
        labels = []
        values = []
    
    return JsonResponse({'labels': labels, 'values': values})


@login_required
def line_chart_data(request):
    """Fetch data for Line Chart (e.g., calories intake for the uploaded food)."""
    latest_entry = FoodDiaryEntry.objects.filter(user=request.user).last()
    if latest_entry:
        # Use the nutrition information for the uploaded food
        labels = ['Calories', 'Carbs', 'Fats', 'Fiber', 'Sugar', 'Protein', 'Sodium', 'Potassium', 'Cholesterol']
        values = [
            latest_entry.calories,
            latest_entry.carbs,
            latest_entry.fats,
            latest_entry.fiber,
            latest_entry.sugar,
            latest_entry.protein,
            latest_entry.sodium,
            latest_entry.potassium,
            latest_entry.cholesterol
        ]
    else:
        labels = []
        values = []
    
    return JsonResponse({'labels': labels, 'values': values})

@login_required
def donut_chart_data(request):
    """Fetch data for Donut Chart (e.g., carbs content of the uploaded food)."""
    latest_entry = FoodDiaryEntry.objects.filter(user=request.user).last()
    if latest_entry:
        # Use the nutrition information for the uploaded food
        labels = ['Calories', 'Carbs', 'Fats', 'Fiber', 'Sugar', 'Protein', 'Sodium', 'Potassium', 'Cholesterol']
        values = [
            latest_entry.calories,
            latest_entry.carbs,
            latest_entry.fats,
            latest_entry.fiber,
            latest_entry.sugar,
            latest_entry.protein,
            latest_entry.sodium,
            latest_entry.potassium,
            latest_entry.cholesterol
        ]
    else:
        labels = []
        values = []
    
    return JsonResponse({'labels': labels, 'values': values})

@login_required
def waterfall_chart_data(request):
    latest_entry = FoodDiaryEntry.objects.filter(user=request.user).last()
    if latest_entry:
        # Use the nutrition information for the uploaded food
        labels = ['Calories', 'Carbs', 'Fats', 'Fiber', 'Sugar', 'Protein', 'Sodium', 'Potassium', 'Cholesterol']
        values = [
            latest_entry.calories,
            latest_entry.carbs,
            latest_entry.fats,
            latest_entry.fiber,
            latest_entry.sugar,
            latest_entry.protein,
            latest_entry.sodium,
            latest_entry.potassium,
            latest_entry.cholesterol
        ]
    else:
        labels = []
        values = []
    
    return JsonResponse({'labels': labels, 'values': values})

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
            # Directly call the function to classify and get nutrition details
            food_details = classify_and_get_nutrition(image_file)

            # Log the food details to check the values
            print("Food Details:", food_details)

            # Check if classification returned valid results
            if not food_details or 'name' not in food_details:
                messages.error(request, "Failed to classify the food. Please try again.")
                return render(request, 'nutriwise/upload_image.html', {'food_details': food_details})

            # Save the entry directly into the database
            FoodDiaryEntry.objects.create(
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
            user_profile.age = int(request.POST.get('age', 0))
            user_profile.gender = request.POST.get('gender', '').capitalize()
            user_profile.height = float(request.POST.get('height', 0.0))
            user_profile.weight = float(request.POST.get('weight', 0.0))
            user_profile.bmi = (
                user_profile.weight / ((user_profile.height / 100) ** 2)
                if user_profile.height > 0 else 0
            )  # Automatically calculate BMI

            user_profile.save()
            messages.success(request, "Profile updated successfully!")
        except ValueError:
            messages.error(request, "Invalid input. Please check your data.")

        return redirect('nutriwise:dashboard2')

    context = {'user_profile': user_profile}
    return render(request, 'nutriwise/profile_update.html', context)

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