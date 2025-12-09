from django.urls import path
from .views import UserProfileListCustomer, UserProfileListBusiness, UserProfileDetail, RegistrationView, CustomLoginView

urlpatterns = [
    path('profiles/customer/', UserProfileListCustomer.as_view(), name='userprofile-customer-list'),
    path('profiles/business/', UserProfileListBusiness().as_view(), name='userprofile-business-list'),
    path('profile/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login')
]
