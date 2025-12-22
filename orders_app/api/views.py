from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from offers_app.models import Offer, OfferDetails
from ..models import Order
from .serializers import OrderSerializer
from user_auth_app.models import UserProfile

class OrdersView(APIView):
    def get(self, request):
        if request.user.type == 'customer':
            orders = Order.objects.filter(customer_user__id=request.user.id)
        elif request.user.type == 'business':
            orders = Order.objects.filter(business_user__id=request.user.id)
        else:
            orders = Order.objects.none()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        offer_details_id = request.data.get('offer_detail_id')
        if offer_details_id is None:
            return Response({"error": "offer_detail_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if offer_details_id not in OfferDetails.objects.values_list('id', flat=True):
            return Response({"error": "Given Offer ID not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.type != 'customer':
            return Response({"detail": "Only customers can create orders."}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
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
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.user.is_staff:
            return Response({'error': 'Permission denied, only staff can delete orders!'}, status=status.HTTP_403_FORBIDDEN)
        
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderCountView(APIView):
    def get(self, request, pk):
        if pk not in UserProfile.objects.values_list('id', flat=True):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated:
            order_count = Order.objects.filter(business_user__id=pk).count()
            return Response({'order_count': order_count}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied, log in to view order count'}, status=status.HTTP_403_FORBIDDEN)
    
class CompletedOrderCountView(APIView):
    def get(self, request, pk):
        if pk not in UserProfile.objects.values_list('id', flat=True):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated:
            completed_order_count = Order.objects.filter(business_user__id=pk, status='completed').count()
            return Response({'completed_order_count': completed_order_count}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied, log in to view completed order count!'}, status=status.HTTP_403_FORBIDDEN)
