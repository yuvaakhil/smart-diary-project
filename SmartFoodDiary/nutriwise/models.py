from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    calorie_goal = models.PositiveIntegerField(default=2000)  # Daily calorie target
    protein_goal = models.FloatField(default=50.0)  # Protein target in grams
    carbs_goal = models.FloatField(default=300.0)  # Carbohydrate target in grams
    fats_goal = models.FloatField(default=70.0)  # Fat target in grams
    enable_notifications = models.BooleanField(default=True)  # Enable/disable notifications
    notify_on_exceed = models.BooleanField(default=False)  # Add this field
    notify_on_deficit = models.BooleanField(default=False)  # Add this field
    diet_type = models.CharField(
        max_length=20,
        choices=[('None', 'None'), ('Vegetarian', 'Vegetarian'), ('Vegan', 'Vegan'), ('Keto', 'Keto'), ('Paleo', 'Paleo')],
        default='None'
    )
    food_restrictions = models.TextField(null=True, blank=True)
    last_notified = models.DateTimeField(null=True, blank=True)

    


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


