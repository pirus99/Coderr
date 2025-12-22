"""
Offers API filters module.

This module provides custom filter classes for filtering offer queryset
based on various criteria like price, delivery time, and creator.
"""

import django_filters
from django.db.models import Min

from ..models import Offer


class OfferFilter(django_filters.FilterSet):
    """
    Filter class for Offer model.

    Provides custom filtering options for offers including minimum price,
    maximum delivery time, and creator ID.
    """
    min_price = django_filters.NumberFilter(label="min-price", method='filter_min_price')
    max_delivery_time = django_filters.NumberFilter(label="max-delivery-time", method='filter_max_delivery_time')
    creator_id = django_filters.NumberFilter(label="creator-id", method='filter_creator_id')

    class Meta:
        model = Offer
        fields = ['user']

    def filter_min_price(self, queryset, name, value):
        """
        Filter offers by minimum price across their offer details.

        Args:
            queryset: The base queryset to filter
            name: The name of the filter parameter
            value: The minimum price value to filter by

        Returns:
            QuerySet: Filtered queryset with offers at or above the minimum price
        """
        return queryset.annotate(min_price=Min('details__price')).filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """
        Filter offers by maximum delivery time in days.

        Args:
            queryset: The base queryset to filter
            name: The name of the filter parameter
            value: The maximum delivery time value to filter by

        Returns:
            QuerySet: Filtered queryset with offers at or below the maximum delivery time
        """
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()

    def filter_creator_id(self, queryset, name, value):
        """
        Filter offers by the creator's user ID.

        Args:
            queryset: The base queryset to filter
            name: The name of the filter parameter
            value: The user ID to filter by

        Returns:
            QuerySet: Filtered queryset with offers created by the specified user
        """
        return queryset.filter(user__id=value)