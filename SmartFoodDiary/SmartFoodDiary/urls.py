from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel URL
    path('accounts/', include('allauth.urls')),  # Allauth URLs for authentication
    path('', include('users.urls', namespace='users')),  # Default users URLs (e.g., login, signup)
    path('nutriwise/', include('nutriwise.urls'))  # Nutriwise app URLs (dashboard, etc.)
]