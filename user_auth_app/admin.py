from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'email', 'type', 'created_at')
    search_fields = ('username', 'email', 'type')
    list_filter = ('type', 'created_at')
