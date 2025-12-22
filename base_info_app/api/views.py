
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from user_auth_app.models import UserProfile
from .serializers import BaseInfo


class BaseInfoListAPIView(APIView):
    serializer_class = BaseInfo
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = BaseInfo(instance={}, many=False)
        return Response(serializer.data)


