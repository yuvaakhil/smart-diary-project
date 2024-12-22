from django.db import models
from nutriwise.models import UserProfile,FoodDiaryEntry
from django.contrib.auth.models import User
from django.utils.timezone import now

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'

