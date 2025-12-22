from rest_framework import serializers
from ..models import Order
from offers_app.models import OfferDetails
from django.shortcuts import get_object_or_404
from user_auth_app.models import UserProfile

class OrderSerializer(serializers.ModelSerializer):

    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetails.objects.all(), write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at', 'offer_detail_id']
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'created_at', 'updated_at']

    def create(self, validated_data):
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            raise serializers.ValidationError({"user": "Authentication is required."})

        customer_user = get_object_or_404(UserProfile, id=request_user.id)
        offer_detail_id = validated_data.pop('offer_detail_id')
        business_user = get_object_or_404(UserProfile, id=offer_detail_id.offer.user.id)

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=offer_detail_id.title,
            revisions=offer_detail_id.revisions,
            delivery_time_in_days=offer_detail_id.delivery_time_in_days,
            price=offer_detail_id.price,
            features=offer_detail_id.features,
            offer_type=offer_detail_id.offer_type,
            status="in_progress"
        )
        return order
    
    def validate(self, attrs):
        """Ensure only 'offer_detail_id' is provided when creating an order via POST."""
        request = self.context['request']
        if request and request.method == 'POST':
            allowed_fields = {'offer_detail_id'}
            unexpected_fields = set(self.initial_data.keys()) - allowed_fields
            if unexpected_fields:
                raise serializers.ValidationError({
                    "non_field_errors": [f"Only 'offer_detail_id' is needed. But got: {', '.join(unexpected_fields)}."]
                })
        return attrs
    
    def update(self, instance, validated_data):
        if set(validated_data.keys()) != {"status"}:
            raise serializers.ValidationError("Only the 'status' field can be updated. Valid values are: 'in_progress', 'completed', 'cancelled'.")
        status = validated_data.pop('status', None)
        instance = super().update(instance, validated_data)
        if status:
            instance.status = status
            instance.save()
        return instance