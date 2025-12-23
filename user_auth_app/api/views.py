"""
User authentication API views module.

This module provides API views for user authentication and profile management.
It includes endpoints for user registration, login, and profile listing/management.
"""

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from user_auth_app.models import UserProfile

from .permissions import IsAdminOrOwnerOrReadOnly
from .serializers import (
    RegistrationSerializer,
    UserCustomerSerializer,
    UserProfileSerializer,
)

class UserProfileListBusiness(generics.ListCreateAPIView):
    """API view for listing and creating business user profiles."""
    queryset = UserProfile.objects.filter(type='business')
    serializer_class = UserProfileSerializer

class UserProfileListCustomer(generics.ListCreateAPIView):
    """API view for listing and creating customer user profiles."""
    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = UserCustomerSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting user profiles."""
    queryset = UserProfile.objects.all()
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    """
    API view for user registration.

    Allows unauthenticated users to create new accounts and receive
    an authentication token upon successful registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user account.

        Args:
            request: HTTP request containing registration data

        Returns:
            Response: Authentication token and user details on success,
                     validation errors on failure
        """
        serializer = RegistrationSerializer(data=request.data)
        status = 201
        data = {}

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.user
            }
        else:
            data = serializer.errors
            status = 400

        return Response(data, status)
    
class CustomLoginView(ObtainAuthToken):
    """
    API view for user login.

    Extends Django REST Framework's ObtainAuthToken to provide
    authentication token and additional user details upon successful login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate a user and return an authentication token.

        Args:
            request: HTTP request containing login credentials

        Returns:
            Response: Authentication token and user details on success,
                     validation errors or account disabled message on failure
        """
        serializer = self.serializer_class(data=request.data)
        status = 200

        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.user
            }
            if not user.is_active:
                return Response({'error': 'User account is disabled.'}, status=403)
        else:
            data = serializer.errors
            status=400

        return Response(data, status)