from django.apps import AppConfig

class AIIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_integration'
    verbose_name = 'AI Integration'

    def ready(self):
        """Perform initialization when the app is ready"""
        try:
            # Import and register signals
            from . import signals

            # Initialize DeepSeek API key
            from django.conf import settings
            if not hasattr(settings, 'DEEPSEEK_API_KEY'):
                import logging
                logger = logging.getLogger('ai.apps')
                logger.warning('DEEPSEEK_API_KEY not found in settings')

            # Register periodic tasks
            from django_celery_beat.models import PeriodicTask, IntervalSchedule
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=1,
                period=IntervalSchedule.DAYS,
            )
            periodic_task, created = PeriodicTask.objects.get_or_create(
                name='cleanup_expired_tasks',
                defaults={
                    'task': 'ai_integration.tasks.cleanup_expired_tasks',
                    'interval': schedule,
                }
            )
            if not created:
                # Update the task and interval if needed
                updated = False
                if periodic_task.task != 'ai_integration.tasks.cleanup_expired_tasks':
                    periodic_task.task = 'ai_integration.tasks.cleanup_expired_tasks'
                    updated = True
                if periodic_task.interval != schedule:
                    periodic_task.interval = schedule
                    updated = True
                if updated:
                    periodic_task.save()

        except Exception as e:
            import logging
            logger = logging.getLogger('ai.apps')
            logger.error(f'Error initializing AI Integration app: {str(e)}')
