
from django.contrib import admin
from users.models import UserProfile  # Import the UserProfile model
from .models import FoodDiaryEntry

@admin.register(FoodDiaryEntry)
class FoodDiaryEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    def image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 100px;"/>')
        return "No image"
# Register the UserProfile model
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'height', 'weight', 'age','food_image', 'prediction_data')
