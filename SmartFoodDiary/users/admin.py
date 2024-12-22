from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    # Display the fields from the User model and UserProfile in the list
    list_display = (
        'user', 'full_name', 'phone_number', 'height', 'weight', 'age', 'gender', 'bmi', 
        'calorie_goal', 'diet_type', 'enable_notifications'
    )

    # Define methods to get the username and email from the related User model
    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email
    
    def calorie_goal(self, obj):
        return obj.calorie_goal

    def diet_type(self, obj):
        return obj.diet_type

    def enable_notifications(self, obj):
        return obj.enable_notifications


    # Define the fields to display in the form when editing a user profile
    fieldsets = (
        (None, {
            'fields': ('user', 'full_name', 'phone_number', 'height', 'weight', 'age', 'gender', 'bmi')
        }),
    )

    # Make sure that the methods are only in list_display and not in fieldsets
    get_username.admin_order_field = 'user__username'  # Allows ordering by username
    get_email.admin_order_field = 'user__email'  # Allows ordering by email

# Register the UserProfile admin (only once)
admin.site.register(UserProfile, UserProfileAdmin)
