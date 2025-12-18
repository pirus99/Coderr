from django.db import models
from offers_app.models import OfferDetails
from user_auth_app.models import UserProfile

class OrderStatus(models.TextChoices):
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class OfferType(models.TextChoices):
    BASIC = 'basic', 'Basic'
    STANDARD = 'standard', 'Standard'
    PREMIUM = 'premium', 'Premium'

class Order(models.Model):
    customer_user = models.ForeignKey(UserProfile, related_name="customer_user", on_delete=models.CASCADE, null=True)
    business_user = models.ForeignKey(UserProfile, related_name='business_user', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField()
    offer_type = models.CharField(max_length=100, choices=OfferType.choices)
    status = models.CharField(max_length=50, choices=OrderStatus.choices, default=OrderStatus.IN_PROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

