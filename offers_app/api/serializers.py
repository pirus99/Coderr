"""
Offers API serializers module.

This module provides serializers for converting Offer and OfferDetails model instances
to/from JSON. It includes serializers for listing, creating, and updating offers with
their associated pricing details.
"""

import os

from rest_framework import serializers

from offers_app.models import Offer, OfferDetails
from user_auth_app.models import UserProfile

class OfferDetailsHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Hyperlinked serializer for OfferDetails.

    Provides a URL field for accessing individual offer detail resources.
    """
    url = serializers.HyperlinkedIdentityField(view_name='offerdetail-detail')

    class Meta:
        model = OfferDetails
        fields = ('id', 'url') 

class OfferDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetails model.

    Provides full details about offer pricing tiers including
    title, revisions, delivery time, price, features, and offer type.
    """

    class Meta:
        model = OfferDetails
        fields = ('id','title','revisions','delivery_time_in_days','price','features','offer_type')

class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for Offer model with computed fields.

    Includes hyperlinked offer details, minimum price, minimum delivery time,
    and user details for the offer creator.
    """
    details = OfferDetailsHyperlinkedSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    def get_min_price(self, obj):
        """
        Return the minimum price among all offer details.

        Args:
            obj: Offer instance

        Returns:
            float: Minimum price or None if no details exist
        """
        details = obj.details.all()
        if details.exists():
            return min(detail.price for detail in details)
        return None
    
    def get_min_delivery_time(self, obj):
        """
        Return the minimum delivery time in days among all offer details.

        Args:
            obj: Offer instance

        Returns:
            int: Minimum delivery time or None if no details exist
        """
        details = obj.details.all()
        if details.exists():
            return min(detail.delivery_time_in_days for detail in details)
        return None
    
    def get_user_details(self, obj):
        """
        Return a dictionary containing the user's first name, last name, and username.

        Args:
            obj: Offer instance

        Returns:
            dict: User details or None if user not found
        """
        user = UserProfile.objects.filter(id=obj.user.id).first()
        if not user:
            return None
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        }
    
    class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description',
                  'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details')

class OfferDetailSerializer(OfferSerializer):
    """
    Detailed serializer for Offer model.

    Extends OfferSerializer to include the user ID field.
    """

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Offer instances with details.

    Requires exactly 3 OfferDetails to be provided with the offer.
    Validates image file extensions.
    """
    details = OfferDetailsSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        """
        Create a new offer with associated details.

        Args:
            validated_data: Dictionary of validated field values

        Returns:
            Offer: The newly created offer instance

        Raises:
            ValidationError: If number of details is not exactly 3
        """
        details_data = validated_data.pop('details', None)
        offer = Offer.objects.create(**validated_data)

        if details_data and len(details_data) != 3:
            raise serializers.ValidationError({"details": "You must provide 3 OfferDetails."})
        if details_data:
            OfferDetails.objects.bulk_create([
                OfferDetails(offer=offer, **detail) for detail in details_data
            ])
        return offer

    def validate_image(self, value):
        """
        Validate that the uploaded image has an allowed extension.

        Args:
            value: The uploaded image file

        Returns:
            File: The validated image file

        Raises:
            ValidationError: If file extension is not jpg, jpeg, or png
        """
        if not value:
            return value
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file. Allowed extensions are {', '.join(valid_extensions)}.")
        return value
    
class OfferUpdateSerializer(OfferSerializer):
    """
    Serializer for updating existing Offer instances.

    Allows updating offer fields and associated details.
    Details must be identified by their offer_type for updates.
    """
    details = OfferDetailsSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        """
        Update an existing offer and its details.

        Args:
            instance: The Offer instance to update
            validated_data: Dictionary of validated field values

        Returns:
            Offer: The updated offer instance

        Raises:
            ValidationError: If offer_type is missing or detail not found
        """
        details_data = validated_data.pop('details', None)
        image = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)

        if image:
            instance.image = image
            instance.save()

        if details_data:
            for detail_data in details_data:
                detail_offer_type = detail_data.get('offer_type', None)
                if detail_offer_type:
                    try:
                        detail_instance = OfferDetails.objects.get(offer=instance, offer_type=detail_offer_type)
                        if detail_instance is not None:
                            if detail_instance.title is not None:
                                detail_instance.title = detail_data.get('title')
                            if detail_instance.revisions is not None:
                                detail_instance.revisions = detail_data.get('revisions')
                            if detail_instance.delivery_time_in_days is not None:
                                detail_instance.delivery_time_in_days = detail_data.get('delivery_time_in_days')
                            if detail_instance.price is not None:
                                detail_instance.price = detail_data.get('price')
                            if detail_instance.features is not None:
                                detail_instance.features = detail_data.get('features')
                            detail_instance.save()
                    except OfferDetails.DoesNotExist:
                        raise serializers.ValidationError({"details": "OfferDetail does not exist."})
                else:
                    raise serializers.ValidationError({"details": "Offer_type for OfferDetail must be provided."})
        return instance
        
    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']