"""
User authentication API permissions module.

This module provides custom permission classes for controlling access
to user profile and authentication-related API endpoints.
"""

from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class for user profile access control.

    Access rules:
    - Any authenticated user: read (GET/HEAD/OPTIONS)
    - POST: only staff/superuser
    - PUT/PATCH/DELETE: only staff/superuser or object owner
    """

    def _is_owner(self, owner, user):
        """Check if the given owner matches the user."""
        if owner is None:
            return False
        if owner == user:
            return True
        owner_pk = getattr(owner, "pk", None) or owner
        user_pk = getattr(user, "pk", None) or user
        return owner_pk == user_pk

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == "POST":
            return bool(user.is_staff or user.is_superuser)

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if user.is_staff or user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        if request.method in ("PUT", "PATCH", "DELETE"):
            owner_attrs = ("owner", "user", "created_by")
            for attr in owner_attrs:
                owner = getattr(obj, attr, None)
                if self._is_owner(owner, user):
                    return True
            try:
                for key in owner_attrs:
                    owner = obj.get(key) if hasattr(obj, "get") else None
                    if self._is_owner(owner, user):
                        return True
            except Exception:
                pass

            return False

        return False