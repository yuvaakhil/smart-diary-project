# recommendations/urls.py
from django.urls import path
from . import views  # Correct import from views.py

urlpatterns = [
    path('statistics/', views.meal_recommendations, name='statistics'),  # Ensure this path is correct
    path('generate-report/', views.generate_pdf_report, name='generate_pdf_report'),
   path('export-csv/', views.export_csv, name='export_csv'),
]
