from django.urls import path, include
from rest_framework import routers
from .views import OffersView, OfferDetailsView, OfferDetailView

router = routers.SimpleRouter()
router.register(r'offerdetails', OfferDetailsView, basename='offerdetail')

urlpatterns = [
    path('', include(router.urls)),
    path('offers/', OffersView.as_view(), name='offers-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offers-detail')
]
