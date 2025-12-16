from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from offers_app.models import Offer, OfferDetails
from .permissions import IsOwnerOrAdminOrReadOnly, IsBusinessUser
from .serializers import OfferSerializer, OfferDetailSerializer, OfferCreateSerializer, OfferDetailsSerializer, OfferUpdateSerializer

class OffersView(APIView):
    permission_classes = [IsBusinessUser]

    def get(self, request):
        self.serializer_class = OfferSerializer
        queryset = Offer.objects.all()
        offers = queryset
        serializer = self.serializer_class(offers, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        self.serializer_class = OfferCreateSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            offer = serializer.save(user_id=request.user.id)
            response_serializer = OfferCreateSerializer(offer, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)
    
class OfferDetailView(APIView):
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get(self, request, pk):
        self.serializer_class = OfferDetailSerializer
        try:
            offer = Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(offer, context={'request': request})
        return Response(serializer.data)
    
    def patch(self, request, pk):
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        try:
            offer = Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
        if self.check_object_permissions(request, offer) is not None:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OfferDetailsView(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetails.objects.all()
    serializer_class = OfferDetailsSerializer