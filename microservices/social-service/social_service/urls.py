from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for service monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'social-service',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/v1/social/accounts/', include('accounts.urls')),
    path('api/v1/social/posts/', include('posts.urls')),
    path('api/v1/social/comments/', include('comments.urls')),
    path('api/v1/social/scheduling/', include('scheduling.urls')),
]