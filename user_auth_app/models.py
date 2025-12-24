from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    user = models.AutoField(primary_key=True)
    id = models.IntegerField(null=True, editable=False, unique=True)
    username = models.CharField(max_length=150, unique=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to='user_files/', blank=True, null=True)
    tel = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.id != self.user:
            self.id = self.user
            super().save(update_fields=['id'])

    def __str__(self):
        return self.username