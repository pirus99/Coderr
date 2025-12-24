"""
Base information API serializers module.

This module provides serializers for retrieving aggregate statistics about the
application, including review metrics, user counts, and offer statistics.
"""

from django.db import models
from rest_framework import serializers

from offers_app.models import Offer
from reviews_app.models import Review
from user_auth_app.models import UserProfile

class BaseInfo(serializers.Serializer):
    """Serializer for base application information and statistics."""
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    business_profile_count = serializers.SerializerMethodField()
    offer_count = serializers.SerializerMethodField()

    class Meta:
        fields = ['review_count', 'average_rating', 'business_profile_count', 'offer_count']

    def get_review_count(self, obj):
        """Return the total count of all reviews."""
        return Review.objects.all().count()
    
    def get_average_rating(self, obj):
        """Calculate and return the average rating across all reviews."""
        reviews = Review.objects.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0.0
    
    def get_business_profile_count(self, obj):
        """Return the total count of business type user profiles."""
        return UserProfile.objects.filter(type='business').count()
    
    def get_offer_count(self, obj):
        """Return the total count of all offers."""
        return Offer.objects.all().count()
