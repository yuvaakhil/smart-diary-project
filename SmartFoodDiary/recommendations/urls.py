# recommendations/urls.py
from django.urls import path
from . import views  # Correct import from views.py

urlpatterns = [
    path('statistics/', views.meal_recommendations, name='statistics'),  # Ensure this path is correct
    # Add any other URLs you need for your app
]
