# nutriwise/urls.py
from django.urls import path
from . import views
from .views import custom_logout


app_name = 'nutriwise'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # This is the default dashboard
    path('dashboard/', views.dashboard, name='dashboard'),  # Keeps the dashboard route for the main dashboard
    path('dashboard2/', views.dashboard2, name='dashboard2'),  # Separate route for dashboard2
    path('update_profile/', views.update_profile, name='update_profile'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('analyze-food/', views.analyze_food_image, name='analyze_food_image'),
    path('profile/', views.profile, name='profile'),
    path('pie_chart_data/', views.pie_chart_data, name='pie_chart_data'),
    path('bar_chart_data/', views.bar_chart_data, name='bar_chart_data'),
    path('line_chart_data/', views.line_chart_data, name='line_chart_data'),
    path('donut_chart_data/', views.donut_chart_data, name='donut_chart_data'),
    path('waterfall_chart_data/', views.waterfall_chart_data, name='waterfall_chart_data'),
    path('logout/', custom_logout, name='custom_logout'),
    
    ]