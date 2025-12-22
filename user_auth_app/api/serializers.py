"""
User authentication API serializers module.

This module provides serializers for user profile management and authentication.
It includes serializers for user registration, profile display, and user data conversion.
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from user_auth_app.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.

    Provides complete user profile information including personal details,
    location, contact information, and account metadata.
    """
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']

    def to_representation(self, instance):
        """
        Convert None and empty values to empty strings in the serialized output.

        Args:
            instance: UserProfile instance to serialize

        Returns:
            dict: Serialized user profile data with None values converted to empty strings
        """
        data = super().to_representation(instance)
        for key, value in list(data.items()):
            if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                data[key] = ''
        return data
    
class UserCustomerSerializer(UserProfileSerializer):
    """
    Serializer for customer user profiles.

    Extends UserProfileSerializer with a custom uploaded_at field
    and limited fields appropriate for customer profiles.
    """
    uploaded_at = serializers.DateTimeField(source='date_joined', read_only=True) 
    class Meta(UserProfileSerializer.Meta):
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type']
    
class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles user account creation with password validation,
    email uniqueness checking, and user type assignment.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True, 
                'min_length': 8
            }
        }

    def save(self):
        """
        Create and save a new user account.

        Validates that:
        - Passwords match
        - Email is unique
        - Username is unique
        - User type is valid ('business' or 'customer')

        Returns:
            UserProfile: The newly created user profile

        Raises:
            ValidationError: If any validation fails
        """
        pw= self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        type = self.validated_data['type']
        users = UserProfile.objects.filter(username=self.validated_data['username'])
        emails = UserProfile.objects.filter(email=self.validated_data['email'])

        if emails.exists():
            raise serializers.ValidationError({'error':'email already in use'})

        if users.exists():
            raise serializers.ValidationError({'error':'username already in use'})

        if pw != repeated_pw:
            raise serializers.ValidationError({'error':'passwords don`t match'})

        if type not in ['business', 'customer']:
            raise serializers.ValidationError({'error':'type must be business or customer'})

        account = UserProfile(email=self.validated_data['email'], username=self.validated_data['username'], type=type)
        account.set_password(pw)
        account.save()
        return account
