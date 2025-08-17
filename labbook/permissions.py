from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Доступ только владельцу. Чтение тоже только владельцу (если хочешь
    разрешить read-only всем — верни True для SAFE_METHODS).
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
