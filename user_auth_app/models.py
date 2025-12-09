#models.py
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

class UserProfile(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds profile fields for business and customer users.
    """
    # Override primary key to use 'user' field name for API compatibility
    user = models.AutoField(primary_key=True)
    
    # Additional profile fields
    location = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(
        upload_to='user_files/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'])],
        help_text='Allowed file types: jpg, jpeg, png, pdf, doc, docx'
    )
    tel = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(
        max_length=50, 
        choices=[('business', 'Business'), ('customer', 'Customer')],
        help_text='User type: business or customer'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username