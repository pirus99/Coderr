"""
Offers API permissions module.

This module provides custom permission classes for controlling access
to offer-related API endpoints.
"""

from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsBusinessUser(permissions.BasePermission):
    """
    Permission class that allows business users to modify resources.

    Safe methods (GET, HEAD, OPTIONS) are allowed for all users.
    Write methods require authenticated business users or superusers.
    """

    def has_permission(self, request, user):
        """
        Check if the user has permission to perform the request.

        Args:
            request: The HTTP request object
            user: The user object (not used, kept for signature compatibility)

        Returns:
            bool: True if permission granted, False otherwise
        """
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and (request.user.type == 'business' or request.user.is_superuser))
    
class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class that restricts write access to object owners and admins.

    - Safe methods require authentication
    - Write methods require authentication and ownership or superuser status
    """

    def has_permission(self, request, view):
        """
        Check if the user has general permission to access the view.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if permission granted, False otherwise
        """
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access a specific object.

        Args:
            request: The HTTP request object
            view: The view being accessed
            obj: The object being accessed

        Returns:
            bool: True if permission granted, False otherwise
        """
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        if not hasattr(request.user, 'is_authenticated') or not request.user.is_authenticated:
            return False
        return bool(request.user == obj.user or request.user.is_superuser)
