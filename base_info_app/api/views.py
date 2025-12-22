"""
Base information API views module.

This module provides API views for retrieving aggregate statistics and base
information about the application, including review counts, ratings, and user statistics.
"""

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from user_auth_app.models import UserProfile
from .serializers import BaseInfo


class BaseInfoListAPIView(APIView):
    """
    API view for retrieving base application statistics.

    Provides aggregate information including review counts, average ratings,
    business profile counts, and offer counts. Accessible to all users.
    """
    serializer_class = BaseInfo
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Retrieve base application statistics.

        Args:
            request: HTTP request

        Returns:
            Response: Dictionary containing aggregate statistics
        """
        serializer = BaseInfo(instance={}, many=False)
        return Response(serializer.data)


