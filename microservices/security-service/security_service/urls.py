from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for service monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'security-service',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/v1/security/auth/', include('authentication.urls')),
    path('api/v1/security/authz/', include('authorization.urls')),
    path('api/v1/security/audit/', include('audit_logs.urls')),
    path('api/v1/security/rate-limit/', include('rate_limiting.urls')),
    path('api/v1/security/encryption/', include('encryption.urls')),
]