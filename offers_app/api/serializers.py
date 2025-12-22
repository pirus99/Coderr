import os
from rest_framework import serializers
from offers_app.models import Offer, OfferDetails
from user_auth_app.models import UserProfile

class OfferDetailsHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='offerdetail-detail')

    class Meta:
        model = OfferDetails
        fields = ('id', 'url') 

class OfferDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetails
        fields = ('id','title','revisions','delivery_time_in_days','price','features','offer_type')

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailsHyperlinkedSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    def get_min_price(self, obj):
        """Return the minimum price among all offer details."""
        details = obj.details.all()
        if details.exists():
            return min(detail.price for detail in details)
        return None
    
    def get_min_delivery_time(self, obj):
        """Return the minimum delivery time in days among all offer details."""
        details = obj.details.all()
        if details.exists():
            return min(detail.delivery_time_in_days for detail in details)
        return None
    
    def get_user_details(self, obj):
        """Return a dictionary containing the user's first name, last name, and username."""
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

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
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
        """Validate that the uploaded image has an allowed extension (jpg, jpeg, or png)."""
        if not value:
            return value
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file. Allowed extensions are {', '.join(valid_extensions)}.")
        return value
    
class OfferUpdateSerializer(OfferSerializer):
    details = OfferDetailsSerializer(many=True, required=False)

    def update(self, instance, validated_data):
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