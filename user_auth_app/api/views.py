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
    queryset = UserProfile.objects.filter(type='business')
    serializer_class = UserProfileSerializer

class UserProfileListCustomer(generics.ListCreateAPIView):
    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
    permission_classes = [AllowAny]

    def post(self, request):
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
        else:
            data = serializer.errors
            status=400

        return Response(data, status)