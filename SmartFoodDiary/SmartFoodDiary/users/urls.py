
from django.urls import path
from . import views
from .views import CustomLoginView

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),  # Ensure this is correct
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
]

