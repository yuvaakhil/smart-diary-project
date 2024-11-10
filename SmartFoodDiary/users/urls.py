from django.urls import path
from . import views  
from .views import CustomLoginView,register
app_name = 'users'  # This is optional but useful if you use reverse URL lookup

urlpatterns = [
   
    path('login/', CustomLoginView.as_view(), name='login'),
     path('register/', register, name='register'),
   
]
