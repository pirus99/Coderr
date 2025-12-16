from django.contrib import admin

# Register your models here.

from .models import Offer, OfferDetails  

admin.site.register(Offer)
admin.site.register(OfferDetails)