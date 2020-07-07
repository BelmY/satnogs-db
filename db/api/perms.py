"""SatNOGS DB API permissions, django rest framework"""
from rest_framework import permissions


class SafeMethodsWithPermission(permissions.BasePermission):
    """Access non-destructive methods (like GET and HEAD) with API Key"""
    def has_permission(self, request, view):
        return self.has_object_permission(request, view)

    def has_object_permission(self, request, view, obj=None):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return True
