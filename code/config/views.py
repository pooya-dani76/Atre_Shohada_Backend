from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .permissions import HasSwaggerAPIKey
from django.http import HttpResponseForbidden
import json
from django.http import JsonResponse



class SecureSwaggerView(SpectacularSwaggerView):
    def dispatch(self, request, *args, **kwargs):
        if not HasSwaggerAPIKey().has_permission(request, self):
            return HttpResponseForbidden(
                json.dumps({"detail": "Access denied: Invalid or missing API key."}),
                content_type="application/json"
            )
        return super().dispatch(request, *args, **kwargs)



class SecureSchemaView(SpectacularAPIView):
    def dispatch(self, request, *args, **kwargs):
        permission = HasSwaggerAPIKey()
        if not permission.has_permission(request, self):
            return JsonResponse(
                {"detail": "Access denied: Invalid or missing API key."},
                status=403
            )
        return super().dispatch(request, *args, **kwargs)
