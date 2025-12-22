from django.urls import path
from .views import ReviewsView, ReviewDetailView

urlpatterns = [
    path('', ReviewsView.as_view(), name='reviews-list'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]
