from django.contrib import admin
from .models import Offer, OfferDetails  

class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'user__username', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at', 'updated_at')

admin.site.register(Offer, OfferAdmin)


class OfferDetailsAdmin(admin.ModelAdmin):
    list_display = ('offer', 'title', 'revisions', 'delivery_time_in_days', 'price')
    search_fields = ('offer__title', 'title')


admin.site.register(OfferDetails, OfferDetailsAdmin)
