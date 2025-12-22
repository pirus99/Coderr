"""
Reviews API views module.

This module provides API views for managing reviews in the application.
It includes endpoints for listing, creating, updating, and deleting reviews.
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews_app.models import Review
from user_auth_app.models import UserProfile

from .permissions import IsBusinessUser, IsCustomerUser, IsOwnerOrAdminOrReadOnly
from .serializers import ReviewCreateSerializer, ReviewSerializer


class ReviewsView(APIView):
	"""
	API view for listing and creating reviews.

	Supports GET requests to retrieve a list of reviews with optional filtering
	and ordering, and POST requests to create new reviews.
	"""

	def get(self, request):
		"""
		Retrieve a list of reviews with optional filtering and ordering.

		Query Parameters:
			business_user_id: Filter reviews by business user ID
			reviewer_id: Filter reviews by reviewer user ID
			ordering: Order results by 'rating', '-rating', 'updated_at', or '-updated_at'

		Returns:
			Response: List of serialized review objects
		"""
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
		"""
		Create a new review.

		Only authenticated customers can create reviews. Each customer can only
		review a business user once.

		Args:
			request: HTTP request containing review data

		Returns:
			Response: Serialized review object on success, errors on failure
		"""
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
	"""
	API view for retrieving, updating, and deleting individual reviews.

	Provides GET, PUT, PATCH, and DELETE methods for managing specific review instances.
	Only the review owner or admin can update or delete a review.
	"""

	def get_object(self, pk):
		"""
		Retrieve a review object by primary key.

		Args:
			pk: Primary key of the review

		Returns:
			Review: Review object if found, None otherwise
		"""
		try:
			return Review.objects.get(pk=pk)
		except Review.DoesNotExist:
			return None

	def get(self, request, pk):
		"""
		Retrieve a specific review by ID.

		Args:
			request: HTTP request
			pk: Primary key of the review

		Returns:
			Response: Serialized review object or error message
		"""
		review = self.get_object(pk)
		if not review:
			return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = ReviewSerializer(review)
		return Response(serializer.data)

	def put(self, request, pk):
		"""
		Fully update a review (all fields required).

		Args:
			request: HTTP request containing updated review data
			pk: Primary key of the review

		Returns:
			Response: Updated review object or error message
		"""
		return self._update(request, pk, partial=False)

	def patch(self, request, pk):
		"""
		Partially update a review (only specified fields updated).

		Args:
			request: HTTP request containing fields to update
			pk: Primary key of the review

		Returns:
			Response: Updated review object or error message
		"""
		return self._update(request, pk, partial=True)

	def _update(self, request, pk, partial):
		"""
		Internal method to handle both PUT and PATCH updates for reviews.

		Args:
			request: HTTP request containing update data
			pk: Primary key of the review
			partial: Boolean indicating if update is partial (PATCH) or full (PUT)

		Returns:
			Response: Updated review object or error message
		"""
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
		"""
		Delete a specific review.

		Only the review owner or admin can delete a review.

		Args:
			request: HTTP request
			pk: Primary key of the review to delete

		Returns:
			Response: 204 No Content on success, error message on failure
		"""
		self.permission_classes = [IsOwnerOrAdminOrReadOnly]
		review = self.get_object(pk)
		if not review:
			return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
		if request.user != review.reviewer and not request.user.is_superuser:
			return Response({'error': 'You do not have permission to delete this review'}, status=status.HTTP_403_FORBIDDEN)
		review.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

