
from django.urls import path

from .views import BaseInfoListAPIView

urlpatterns = [
	path('', BaseInfoListAPIView.as_view(), name='baseinfo-list'),
]
