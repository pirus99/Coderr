"""
Base information API URL configuration.

This module defines URL patterns for the base information API endpoints,
providing access to application-wide statistics and metrics.
"""

from django.urls import path

from .views import BaseInfoListAPIView

urlpatterns = [
    path('', BaseInfoListAPIView.as_view(), name='baseinfo-list'),
]
