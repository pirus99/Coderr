"""
Reviews API URL configuration.

This module defines URL patterns for the reviews API endpoints,
mapping URLs to their corresponding view classes.
"""

from django.urls import path

from .views import ReviewDetailView, ReviewsView

urlpatterns = [
    path('', ReviewsView.as_view(), name='reviews-list'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]
