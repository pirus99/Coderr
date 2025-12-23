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
    """
    Serializer for base application information and statistics.

    Provides computed fields for review count, average rating,
    business profile count, and offer count.
    """
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    business_profile_count = serializers.SerializerMethodField()
    offer_count = serializers.SerializerMethodField()

    class Meta:
        fields = ['review_count', 'average_rating', 'business_profile_count', 'offer_count']

    def get_review_count(self, obj):
        """
        Return the total count of all reviews in the system.

        Args:
            obj: Not used (required by SerializerMethodField)

        Returns:
            int: Total number of reviews
        """
        return Review.objects.all().count()
    
    def get_average_rating(self, obj):
        """
        Calculate and return the average rating across all reviews.

        Args:
            obj: Not used (required by SerializerMethodField)

        Returns:
            float: Average rating rounded to 2 decimal places, or 0.0 if no reviews exist
        """
        reviews = Review.objects.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0.0
    
    def get_business_profile_count(self, obj):
        """
        Return the total count of business type user profiles.

        Args:
            obj: Not used (required by SerializerMethodField)

        Returns:
            int: Number of business user profiles
        """
        return UserProfile.objects.filter(type='business').count()
    
    def get_offer_count(self, obj):
        """
        Return the total count of all offer details in the system.

        Args:
            obj: Not used (required by SerializerMethodField)

        Returns:
            int: Total number of offer details
        """
        return Offer.objects.all().count()
