import os
import psutil
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring service status
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Perform comprehensive health check
        """
        health_status = {
            'service': 'content-service',
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'checks': {}
        }
        
        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            health_status['checks']['database'] = {
                'status': 'healthy',
                'response_time_ms': self._measure_db_response_time()
            }
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Cache check
        try:
            cache_key = 'health_check_test'
            cache.set(cache_key, 'test_value', 30)
            cached_value = cache.get(cache_key)
            if cached_value == 'test_value':
                health_status['checks']['cache'] = {'status': 'healthy'}
            else:
                raise Exception('Cache value mismatch')
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # System resources check
        try:
            disk_usage = psutil.disk_usage('/')
            memory = psutil.virtual_memory()
            
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            memory_available_mb = memory.available / (1024 * 1024)
            
            health_status['checks']['system'] = {
                'status': 'healthy',
                'disk_usage_percent': round(disk_percent, 2),
                'memory_available_mb': round(memory_available_mb, 2)
            }
            
            # Check against thresholds
            if disk_percent > settings.HEALTH_CHECK['DISK_USAGE_MAX']:
                health_status['status'] = 'degraded'
                health_status['checks']['system']['status'] = 'warning'
                health_status['checks']['system']['warning'] = 'High disk usage'
            
            if memory_available_mb < settings.HEALTH_CHECK['MEMORY_MIN']:
                health_status['status'] = 'degraded'
                health_status['checks']['system']['status'] = 'warning'
                health_status['checks']['system']['warning'] = 'Low memory available'
                
        except Exception as e:
            health_status['checks']['system'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Determine overall status code
        if health_status['status'] == 'healthy':
            return Response(health_status, status=status.HTTP_200_OK)
        elif health_status['status'] == 'degraded':
            return Response(health_status, status=status.HTTP_200_OK)
        else:
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    def _measure_db_response_time(self):
        """Measure database response time in milliseconds"""
        import time
        start_time = time.time()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM django_migrations')
                cursor.fetchone()
        except:
            pass
        end_time = time.time()
        return round((end_time - start_time) * 1000, 2)


class ServiceInfoView(APIView):
    """
    Service information endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return service information and capabilities
        """
        service_info = {
            'service': 'content-service',
            'version': '1.0.0',
            'description': 'Content management, posts, media, and scheduling service',
            'capabilities': [
                'post_management',
                'media_upload',
                'content_templates',
                'post_scheduling',
                'content_analytics'
            ],
            'endpoints': {
                'posts': '/api/v1/posts/',
                'media': '/api/v1/media/',
                'templates': '/api/v1/templates/',
                'scheduling': '/api/v1/scheduling/',
                'analytics': '/api/v1/analytics/'
            },
            'supported_platforms': [
                'facebook',
                'instagram',
                'twitter',
                'linkedin',
                'youtube',
                'tiktok'
            ],
            'supported_media_types': {
                'images': settings.ALLOWED_IMAGE_TYPES,
                'videos': settings.ALLOWED_VIDEO_TYPES
            },
            'limits': {
                'max_upload_size_mb': settings.MAX_UPLOAD_SIZE // (1024 * 1024),
                'max_post_length': settings.MAX_POST_LENGTH,
                'max_hashtags': settings.MAX_HASHTAGS
            },
            'environment': {
                'debug': settings.DEBUG,
                'timezone': settings.TIME_ZONE,
                'database': 'postgresql' if 'postgresql' in settings.DATABASES['default']['ENGINE'] else 'other',
                'cache': 'redis' if 'redis' in settings.CACHES['default']['LOCATION'] else 'other'
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return Response(service_info, status=status.HTTP_200_OK)