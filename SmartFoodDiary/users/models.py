from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='users_profile' )
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional phone number
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # in cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # in kg
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True,
    )
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # BMI value
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
    
    def calculate_bmi(self):
        """
        Calculate BMI using the formula: BMI = weight (kg) / height (m)^2
        """
        if self.weight and self.height and self.height > 0:
            height_in_meters = self.height / 100  # Convert height from cm to meters
            return round(self.weight / (height_in_meters ** 2), 2)
        return None

    def save(self, *args, **kwargs):
        """
        Override save to calculate BMI before saving the profile.
        """
        self.bmi = self.calculate_bmi()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"
