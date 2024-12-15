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
