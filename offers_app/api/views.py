"""
Offers API views module.

This module provides API views for managing offers and offer details in the application.
It includes endpoints for listing, creating, updating, and deleting offers and their associated details.
"""

from rest_framework import generics, status, viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer, OfferDetails

from .filters import OfferFilter
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOwnerOrAdminOrReadOnly
from .serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferDetailsSerializer,
    OfferSerializer,
    OfferUpdateSerializer,
)

class OffersView(generics.ListCreateAPIView):
    """
    API view for listing and creating offers.

    Supports filtering, pagination, searching, and ordering of offers.
    Only business users can create offers.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsBusinessUser]
    pagination_class = OfferPagination
    filterset_class = OfferFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at']
    
    def post(self, request):
        """
        Create a new offer with associated details.

        Args:
            request: HTTP request containing offer data

        Returns:
            Response: Serialized offer object on success, errors on failure
        """
        self.serializer_class = OfferCreateSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            offer = serializer.save(user_id=request.user.id)
            response_serializer = OfferCreateSerializer(offer, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)
    
class OfferDetailView(APIView):
    """
    API view for retrieving, updating, and deleting individual offers.

    Provides GET, PATCH, and DELETE methods for managing specific offer instances.
    Only the offer owner or admin can update or delete an offer.
    """
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get(self, request, pk):
        """
        Retrieve a specific offer by ID with all its details.

        Args:
            request: HTTP request
            pk: Primary key of the offer

        Returns:
            Response: Serialized offer object or error message
        """
        self.serializer_class = OfferDetailSerializer
        try:
            offer = Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(offer, context={'request': request})
        return Response(serializer.data)
    
    def patch(self, request, pk):
        """
        Partially update an offer and its details.

        Args:
            request: HTTP request containing fields to update
            pk: Primary key of the offer

        Returns:
            Response: Updated offer object or error message
        """
        self.serializer_class = OfferUpdateSerializer
        try:
            offer = Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
        if self.check_object_permissions(request, offer) is not None:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(offer, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        """
        Delete a specific offer.

        Only the offer owner or admin can delete an offer.

        Args:
            request: HTTP request
            pk: Primary key of the offer to delete

        Returns:
            Response: 204 No Content on success, error message on failure
        """
        try:
            offer = Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
        if self.check_object_permissions(request, offer) is not None:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OfferDetailsView(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API viewset for offer details.

    Provides list and retrieve actions for OfferDetails model instances.
    """
    queryset = OfferDetails.objects.all()
    serializer_class = OfferDetailsSerializer