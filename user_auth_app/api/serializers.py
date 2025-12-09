from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key, value in list(data.items()):
            if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                data[key] = ''
        return data
    
class RegistrationSerializer(serializers.ModelSerializer):

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
