from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews_app.models import Review
from user_auth_app.api.serializers import UserProfileSerializer
from user_auth_app.models import UserProfile


class ReviewSerializer(serializers.ModelSerializer):
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['business_user', 'reviewer', 'rating', 'description']
        read_only_fields = ['reviewer']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('rating must be between 1 and 5')
        return value
    
    def validate(self, attrs):
        return super().validate(attrs)
    
    def create(self, validated_data):
        request_user = self.context['request'].user
        reviewer = get_object_or_404(UserProfile, id=request_user.id)
        review = Review.objects.create(
            business_user=validated_data['business_user'],
            reviewer=reviewer,
            rating=validated_data['rating'],
            description=validated_data.get('description', '')
        )
        return review
    
    