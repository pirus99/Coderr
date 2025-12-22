import django_filters
from django.db.models import Min
from ..models import Offer


class OfferFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(label="min-price", method='filter_min_price')
    max_delivery_time = django_filters.NumberFilter(label="max-delivery-time", method='filter_max_delivery_time')
    creator_id = django_filters.NumberFilter(label="creator-id", method='filter_creator_id')

    class Meta:
        model = Offer
        fields = ['user']

    def filter_min_price(self, queryset, name, value):
        """Filter offers by minimum price across their offer details."""
        return queryset.annotate(min_price=Min('details__price')).filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """Filter offers by maximum delivery time in days."""
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()

    def filter_creator_id(self, queryset, name, value):
        """Filter offers by the creator's user ID."""
        return queryset.filter(user__id=value)