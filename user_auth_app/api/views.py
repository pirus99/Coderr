from .permissions import IsAdminOrOwnerOrReadOnly
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from user_auth_app.models import UserProfile
from .serializers import RegistrationSerializer, UserProfileSerializer

class UserProfileListBusiness(generics.ListCreateAPIView):
    """API endpoint for listing and creating business user profiles."""
    queryset = UserProfile.objects.filter(type='business')
    serializer_class = UserProfileSerializer

class UserProfileListCustomer(generics.ListCreateAPIView):
    """API endpoint for listing and creating customer user profiles."""
    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting user profiles."""
    queryset = UserProfile.objects.all()
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    """API endpoint for user registration."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            return Response({
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.user
            }, status=201)
        
        return Response(serializer.errors, status=400)
    
class CustomLoginView(ObtainAuthToken):
    """API endpoint for user login with token generation."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.user
            }, status=200)
        
        return Response(serializer.errors, status=400)