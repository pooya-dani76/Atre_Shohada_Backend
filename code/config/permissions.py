from rest_framework.permissions import BasePermission
import os


class HasSwaggerAPIKey(BasePermission):
    def has_permission(self, request, view):
        expected_key = os.getenv("DATABASE_API_KEY")
        provided_key = request.headers.get("X-API-KEY") or request.GET.get("api_key")
        
        if provided_key != expected_key:
            return False
        return True

