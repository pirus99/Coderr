from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsBusinessUser(permissions.BasePermission):

    def has_permission(self, request, user):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and (request.user.type == 'business' or request.user.is_superuser))
    
class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        if not hasattr(request.user, 'is_authenticated') or not request.user.is_authenticated:
            return False
        return bool(request.user == obj.user or request.user.is_superuser)
