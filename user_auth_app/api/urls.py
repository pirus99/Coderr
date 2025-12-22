"""
User authentication API URL configuration.

This module defines URL patterns for user authentication and profile management
API endpoints, mapping URLs to their corresponding view classes.
"""

from django.urls import path

from .views import (
    CustomLoginView,
    RegistrationView,
    UserProfileDetail,
    UserProfileListBusiness,
    UserProfileListCustomer,
)

urlpatterns = [
    path('profiles/customer/', UserProfileListCustomer.as_view(), name='userprofile-customer-list'),
    path('profiles/business/', UserProfileListBusiness.as_view(), name='userprofile-business-list'),
    path('profile/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login')
]
