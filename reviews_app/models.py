from django.db import models
from user_auth_app.models import UserProfile

class Review(models.Model):
    business_user = models.ForeignKey(UserProfile, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(UserProfile, related_name='given_reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
