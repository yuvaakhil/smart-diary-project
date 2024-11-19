# smartfooddiary/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Ensure 'users' is the correct path prefix
    path('accounts/', include('allauth.urls')),
]