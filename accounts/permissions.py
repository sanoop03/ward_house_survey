from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow access only to users with role='admin'."""

    message = "Access restricted to admin users only."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.role == 'admin'
        )


class IsFieldAgentRole(BasePermission):
    """Allow access only to users with role='field_agent'."""

    message = "Access restricted to field agents only."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.role == 'field_agent'
        )
