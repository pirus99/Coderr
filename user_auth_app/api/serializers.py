from rest_framework import serializers
from user_auth_app.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model with read operations."""
    
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']
        read_only_fields = ['user', 'created_at']

    def to_representation(self, instance):
        """Convert None and empty values to empty strings for API consistency."""
        data = super().to_representation(instance)
        for key, value in list(data.items()):
            if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                data[key] = ''
        return data
    
class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation."""
    
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True, 
                'min_length': 8,
                'style': {'input_type': 'password'}
            }
        }

    def validate_type(self, value):
        """Validate that type is either 'business' or 'customer'."""
        if value not in ['business', 'customer']:
            raise serializers.ValidationError('Type must be either "business" or "customer".')
        return value

    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        """Create new user with hashed password."""
        # Remove repeated_password as it's not a model field
        validated_data.pop('repeated_password')
        
        # Create user with proper password hashing
        user = UserProfile.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data['type']
        )
        return user
