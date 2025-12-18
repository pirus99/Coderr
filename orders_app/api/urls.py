from django.urls import path, include
from rest_framework import routers
from ..models import Order
from .views import OrdersView, OrderCountView, CompletedOrderCountView

urlpatterns = [
    path('orders/', OrdersView.as_view(), name='orders-list'),
    path('orders/<int:pk>/', OrdersView.as_view(), name='orders-detail'),
    path('order-count/<int:pk>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:pk>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
]