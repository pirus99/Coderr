from django.contrib import admin

from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_user', 'business_user', 'status', 'created_at')

admin.site.register(Order, OrderAdmin)
