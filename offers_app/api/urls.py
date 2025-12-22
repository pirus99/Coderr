"""
Offers API URL configuration.

This module defines URL patterns for the offers API endpoints,
mapping URLs to their corresponding view classes and viewsets.
"""

from django.urls import include, path
from rest_framework import routers

from .views import OfferDetailView, OfferDetailsView, OffersView

router = routers.SimpleRouter()
router.register(r'offerdetails', OfferDetailsView, basename='offerdetail')

urlpatterns = [
    path('', include(router.urls)),
    path('offers/', OffersView.as_view(), name='offers-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offers-detail')
]
