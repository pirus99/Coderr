from rest_framework import serializers
from django.db import models

from offers_app.models import OfferDetails
from reviews_app.models import Review
from user_auth_app.models import UserProfile

class BaseInfo(serializers.Serializer):
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    business_profile_count = serializers.SerializerMethodField()
    offer_count = serializers.SerializerMethodField()

    class Meta:
        fields = ['review_count', 'average_rating', 'business_profile_count', 'offer_count']

    def get_review_count(self, obj):
        return Review.objects.all().count()
    
    def get_average_rating(self, obj):
        reviews = Review.objects.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0.0
    
    def get_business_profile_count(self, obj):
        return UserProfile.objects.filter(type='business').count()
    
    def get_offer_count(self, obj):
        return OfferDetails.objects.all().count()
