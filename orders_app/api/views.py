"""
Orders API views module.

This module provides API views for managing orders in the application.
It includes endpoints for listing, creating, updating, and deleting orders,
as well as retrieving order statistics.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer, OfferDetails
from user_auth_app.models import UserProfile

from ..models import Order
from .serializers import OrderSerializer

class OrdersView(APIView):
    """
    API view for managing orders.

    Supports GET requests to retrieve filtered order lists based on user type,
    POST requests to create new orders, PATCH requests to update order status,
    and DELETE requests to remove orders (staff only).
    """

    def get(self, request):
        """
        Retrieve orders filtered by user type.

        Customer users see their placed orders, business users see orders
        for their offers, and other user types see no orders.

        Args:
            request: HTTP request

        Returns:
            Response: List of serialized order objects
        """
        if request.user.type == 'customer':
            orders = Order.objects.filter(customer_user__id=request.user.id)
        elif request.user.type == 'business':
            orders = Order.objects.filter(business_user__id=request.user.id)
        else:
            orders = Order.objects.none()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new order from an offer detail.

        Only customer users can create orders. Requires an offer_detail_id.

        Args:
            request: HTTP request containing order data

        Returns:
            Response: Serialized order object on success, errors on failure
        """
        offer_details_id = request.data.get('offer_detail_id')
        if isinstance(offer_details_id, str):
            try:
                offer_details_id = int(offer_details_id)
            except ValueError:
                return Response({"error": "offer_detail_id must be a number."}, status=status.HTTP_400_BAD_REQUEST)
        if offer_details_id is None:
            return Response({"error": "offer_detail_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if offer_details_id not in OfferDetails.objects.values_list('id', flat=True):
            return Response({"error": "Given Offer Detail ID not found."}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.type == 'business':
            return Response({"detail": "Only customers can create orders."}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        """
        Update order status.

        Only the business user associated with the order can update its status.

        Args:
            request: HTTP request containing status update
            pk: Primary key of the order

        Returns:
            Response: Updated order object or error message
        """
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.type != 'business' or order.business_user.id != request.user.id:
            return Response({'error': 'Permission denied, you need to be the creator of the related offer to change order Status!'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderSerializer(order, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete an order.

        Only staff members can delete orders.

        Args:
            request: HTTP request
            pk: Primary key of the order to delete

        Returns:
            Response: 204 No Content on success, error message on failure
        """
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.user.is_staff:
            return Response({'error': 'Permission denied, only staff can delete orders!'}, status=status.HTTP_403_FORBIDDEN)
        
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderCountView(APIView):
    """API view for retrieving the total count of orders for a business user."""

    def get(self, request, pk):
        """Get the total number of orders for a specific business user."""
        if pk not in UserProfile.objects.values_list('id', flat=True):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated:
            order_count = Order.objects.filter(business_user__id=pk).exclude(status='completed').count()
            return Response({'order_count': order_count}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied, log in to view order count'}, status=status.HTTP_403_FORBIDDEN)
    
class CompletedOrderCountView(APIView):
    """API view for retrieving the count of completed orders for a business user."""

    def get(self, request, pk):
        """Get the number of completed orders for a specific business user."""
        if pk not in UserProfile.objects.values_list('id', flat=True):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated:
            completed_order_count = Order.objects.filter(business_user__id=pk, status='completed').count()
            return Response({'completed_order_count': completed_order_count}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied, log in to view completed order count!'}, status=status.HTTP_403_FORBIDDEN)
