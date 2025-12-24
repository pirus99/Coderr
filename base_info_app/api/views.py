"""
Base information API views module.

This module provides API views for retrieving aggregate statistics and base
information about the application, including review counts, ratings, and user statistics.
"""

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import BaseInfo


class BaseInfoListAPIView(APIView):
    """API view for retrieving base application statistics."""
    serializer_class = BaseInfo
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Retrieve base application statistics."""
        serializer = BaseInfo(instance={}, many=False)
        return Response(serializer.data)


