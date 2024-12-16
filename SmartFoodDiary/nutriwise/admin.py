from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import FoodDiaryEntry


# FoodDiaryEntryAdmin definition
@admin.register(FoodDiaryEntry)
class FoodDiaryEntryAdmin(admin.ModelAdmin):
    list_display = ['food_name', 'timestamp', 'calories', 'carbs', 'fats', 'fiber', 'sugar', 'protein', 'sodium', 'potassium', 'cholesterol']

    def image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 100px;"/>')
        return "No image"
