"""
Offers API pagination module.

This module provides custom pagination classes for controlling
the number of results returned in offer list views.
"""

from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """
    Custom pagination class for offer list views.

    Configures page size, allows clients to specify custom page size,
    and sets a maximum page size limit.

    Attributes:
        page_size (int): Default number of offers per page
        page_size_query_param (str): Query parameter for custom page size
        max_page_size (int): Maximum allowed page size
    """

    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50