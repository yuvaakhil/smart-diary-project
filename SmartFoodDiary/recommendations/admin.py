from django.contrib import admin
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'sent_at', 'is_read', 'created_at')
    list_filter = ('is_read', 'sent_at', 'created_at')
    search_fields = ('user__username', 'message')


# Register your models here.
