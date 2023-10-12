from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    """Permission for author."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
