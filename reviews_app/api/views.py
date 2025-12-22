from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews_app.models import Review
from user_auth_app.models import UserProfile
from .permissions import IsOwnerOrAdminOrReadOnly, IsBusinessUser, IsCustomerUser
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewsView(APIView):

	def get(self, request):
		qs = Review.objects.all()
		business_user_id = request.query_params.get('business_user_id')
		reviewer_id = request.query_params.get('reviewer_id')
		ordering = request.query_params.get('ordering')
		if ordering in ['rating', '-rating', 'updated_at', '-updated_at']:
			qs = qs.order_by(ordering)
		if business_user_id:
			qs = qs.filter(business_user__id=business_user_id)
		if reviewer_id:
			qs = qs.filter(reviewer__id=reviewer_id)
		serializer = ReviewSerializer(qs, many=True)
		return Response(serializer.data)

	def post(self, request):
		serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
		if not request.user or not request.user.is_authenticated:
			return Response({'detail': 'Authentication required to create reviews'}, status=status.HTTP_403_FORBIDDEN)
		if Review.objects.filter(business_user__id=request.data.get('business_user'), reviewer__id=request.user.id).exists():
			if Review.objects.get(business_user__id=request.data.get('business_user'), reviewer__id=request.user.id):
				return Response({'detail': 'You have already reviewed this business user'}, status=status.HTTP_403_FORBIDDEN)
		if request.user.type != 'customer':
			return Response({'detail': 'Only customers can create reviews'}, status=status.HTTP_403_FORBIDDEN)
		if self.request.data.get('business_user') and UserProfile.objects.filter(id=request.data.get('business_user')).exists():
			business_user = UserProfile.objects.get(id=request.data.get('business_user'))
			if business_user.type != 'business':
				return Response({'detail': 'You can only review business users'}, status=status.HTTP_400_BAD_REQUEST)
		if serializer.is_valid():
			review = serializer.save()
			return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):

	def get_object(self, pk):
		try:
			return Review.objects.get(pk=pk)
		except Review.DoesNotExist:
			return None

	def get(self, request, pk):
		review = self.get_object(pk)
		if not review:
			return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = ReviewSerializer(review)
		return Response(serializer.data)

	def put(self, request, pk):
		return self._update(request, pk, partial=False)

	def patch(self, request, pk):
		return self._update(request, pk, partial=True)

	def _update(self, request, pk, partial):
		self.permission_classes = [IsOwnerOrAdminOrReadOnly]
		review = self.get_object(pk)
		if not review:
			return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
		if request.user != review.reviewer and not request.user.is_superuser:
			return Response({'error': 'You do not have permission to edit this review'}, status=status.HTTP_403_FORBIDDEN)
		serializer = ReviewCreateSerializer(review, data=request.data, partial=partial, context={'request': request})
		if serializer.is_valid():
			updated = serializer.save()
			response = ReviewSerializer(updated).data
			return Response(response, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk):
		self.permission_classes = [IsOwnerOrAdminOrReadOnly]
		review = self.get_object(pk)
		if not review:
			return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
		if request.user != review.reviewer and not request.user.is_superuser:
			return Response({'error': 'You do not have permission to delete this review'}, status=status.HTTP_403_FORBIDDEN)
		review.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

