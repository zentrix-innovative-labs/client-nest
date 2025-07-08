import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_service.settings')

# Create Celery app instance
app = Celery('content_service')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery configuration
app.conf.update(
    # Task routing
    task_routes={
        'content_service.posts.tasks.*': {'queue': 'posts'},
        'content_service.media.tasks.*': {'queue': 'media'},
        'content_service.scheduling.tasks.*': {'queue': 'scheduling'},
        'content_service.content_analytics.tasks.*': {'queue': 'analytics'},
    },
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'process-scheduled-posts': {
            'task': 'scheduling.tasks.process_scheduled_posts',
            'schedule': 60.0,  # Every minute
        },
        'cleanup-expired-media': {
            'task': 'media.tasks.cleanup_expired_media',
            'schedule': 3600.0,  # Every hour
        },
        'generate-content-analytics': {
            'task': 'content_analytics.tasks.generate_daily_analytics',
            'schedule': 86400.0,  # Daily
        },
        'optimize-media-storage': {
            'task': 'media.tasks.optimize_media_storage',
            'schedule': 21600.0,  # Every 6 hours
        },
    },
    
    # Result backend
    result_expires=3600,
    result_persistent=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
    return 'Content Service Celery is working!'