from django import forms
from .models import FoodDiaryEntry

class FoodDiaryEntryForm(forms.ModelForm):
    class Meta:
        model = FoodDiaryEntry
        fields = ['title', 'image', ]

from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'height', 'weight']

class ImageUploadForm(forms.Form):
    image = forms.ImageField()