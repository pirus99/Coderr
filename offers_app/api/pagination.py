"""
Offers API pagination module.

This module provides custom pagination classes for controlling
the number of results returned in offer list views.
"""

from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Custom pagination class for offer list views."""

    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50