from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'content-service',
        'version': '1.0.0-minimal'
    })

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include('posts.urls_minimal')),
] 