"""
Reviews API serializers module.

This module provides serializers for converting Review model instances to/from JSON.
It includes both read and write serializers for different review operations.
"""

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews_app.models import Review
from user_auth_app.api.serializers import UserProfileSerializer
from user_auth_app.models import UserProfile


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reading Review model instances.

    Provides a read-only representation of review data including
    business_user and reviewer as primary keys.
    """
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Review model instances.

    Handles validation and creation of reviews, automatically assigning
    the reviewer from the authenticated user.
    """

    class Meta:
        model = Review
        fields = ['business_user', 'reviewer', 'rating', 'description']
        read_only_fields = ['reviewer']

    def validate_rating(self, value):
        """
        Validate that the rating is between 1 and 5 inclusive.

        Args:
            value: The rating value to validate

        Returns:
            int: The validated rating value

        Raises:
            ValidationError: If rating is not between 1 and 5
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError('rating must be between 1 and 5')
        return value
    
    def validate(self, attrs):
        """
        Perform object-level validation on review data.

        Args:
            attrs: Dictionary of field values

        Returns:
            dict: Validated attributes
        """
        return super().validate(attrs)
    
    def create(self, validated_data):
        """
        Create a new review instance.

        Automatically assigns the reviewer from the authenticated user
        in the request context.

        Args:
            validated_data: Dictionary of validated field values

        Returns:
            Review: The newly created review instance
        """
        request_user = self.context['request'].user
        reviewer = get_object_or_404(UserProfile, id=request_user.id)
        review = Review.objects.create(
            business_user=validated_data['business_user'],
            reviewer=reviewer,
            rating=validated_data['rating'],
            description=validated_data.get('description', '')
        )
        return review
    
    