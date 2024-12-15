from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    food_image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    prediction_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class FoodDiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)  # Title of the diary entry
    image = models.ImageField(upload_to='food_images/')  # Field for uploading images
    description = models.TextField(blank=True, null=True)  # Optional description
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    api_response = models.JSONField(blank=True, null=True)  # Field to store API response

    def __str__(self):
        return self.title
from django.db import models
from django.contrib.auth.models import User

class FoodAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="food_analyses")
    analysis_id = models.CharField(max_length=100, unique=True)
    food_name = models.CharField(max_length=255)
    confidence = models.FloatField()
    nutrition_grade = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    nutrition_details = models.JSONField(default=dict)  # Stores nutrition data as JSON
    ingredients = models.JSONField(default=list)  # Stores ingredients as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_name} (User: {self.user.username})"
