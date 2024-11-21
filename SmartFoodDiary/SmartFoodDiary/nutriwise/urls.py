from django.urls import path
from . import views

app_name = 'nutriwise'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  
]
