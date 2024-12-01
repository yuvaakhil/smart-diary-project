from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

app_name = 'users'

urlpatterns = [
     path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),  # Ensure this is correct
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('check_email/', views.check_email, name='check_email'),
     
     
]