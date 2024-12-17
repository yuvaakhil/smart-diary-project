from django.db import models
from django.contrib.auth.models import User
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=200)
    food_image = models.ImageField(upload_to='food_images/')  # image field
    calories = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    fiber = models.FloatField()
    sugar = models.FloatField()
    protein = models.FloatField()
    sodium = models.FloatField()
    potassium = models.FloatField()
    cholesterol = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.food_name

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    report_data = models.JSONField()  # Store report data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for {self.user.username} - {self.name}"
