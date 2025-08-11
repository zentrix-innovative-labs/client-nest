from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for service monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'queue-service',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/v1/queue/tasks/', include('task_management.urls')),
    path('api/v1/queue/jobs/', include('job_scheduling.urls')),
    path('api/v1/queue/messages/', include('message_broker.urls')),
    path('api/v1/queue/workers/', include('worker_management.urls')),
    path('django-rq/', include('django_rq.urls')),
    path('api/', include('api.urls')),
]