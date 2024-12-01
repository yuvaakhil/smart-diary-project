# urls.py
from django.urls import path
from . import views

app_name = 'nutriwise'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # This is the default dashboard
    path('dashboard/', views.dashboard, name='dashboard'),  # Keeps the dashboard route for the main dashboard
    path('dashboard2/', views.dashboard2, name='dashboard2'),  # Separate route for dashboard2
    path('profile/', views.update_profile, name='profile'),
]