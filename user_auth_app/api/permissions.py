from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    """
    - Any authenticated user: read (GET/HEAD/OPTIONS)
    - POST: only staff/superuser
    - PUT/PATCH (and DELETE): only staff/superuser or object owner
    """

    def _is_owner(self, owner, user):
        if owner is None:
            return False
        # direct compare (owner may be a user instance)
        if owner == user:
            return True
        # compare PKs if available (owner might be a model or an id)
        owner_pk = getattr(owner, "pk", None) or owner
        user_pk = getattr(user, "pk", None) or user
        return owner_pk == user_pk

    def has_permission(self, request, view):
        user = request.user
        # require authentication for all actions
        if not (user and user.is_authenticated):
            return False

        # Allow safe methods for any authenticated user
        if request.method in SAFE_METHODS:
            return True

        # Only staff/superuser can create (POST)
        if request.method == "POST":
            return bool(user.is_staff or user.is_superuser)

        # For other non-object-level methods, allow authenticated users (object-level will restrict)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # staff/superuser always allowed
        if user.is_staff or user.is_superuser:
            return True

        # Allow safe methods for authenticated users
        if request.method in SAFE_METHODS:
            return True

        # For write operations that should be owner-only
        if request.method in ("PUT", "PATCH", "DELETE"):
            owner_attrs = ("owner", "user", "created_by")
            # check attributes on object
            for attr in owner_attrs:
                owner = getattr(obj, attr, None)
                if self._is_owner(owner, user):
                    return True
            # if object is dict-like (e.g. serializer.data)
            try:
                for key in owner_attrs:
                    owner = obj.get(key) if hasattr(obj, "get") else None
                    if self._is_owner(owner, user):
                        return True
            except Exception:
                pass

            return False

        # Default deny for other methods
        return False