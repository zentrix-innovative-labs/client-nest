"""
Service Discovery and Monitoring Integration for AI Service
Handles service registration, health checks, and inter-service communication
"""

import requests
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

class ServiceDiscovery:
    """Service discovery and registration system"""
    
    def __init__(self):
        self.service_name = 'ai-service'
        self.service_port = 8005
        self.service_url = f"http://localhost:{self.service_port}"
        self.registered_services = {}
        self.health_check_interval = 30  # seconds
    
    def register_service(self) -> Dict:
        """Register this service with the service registry"""
        registration_data = {
            'service_name': self.service_name,
            'service_url': self.service_url,
            'health_endpoint': f"{self.service_url}/health/",
            'api_endpoints': [
                f"{self.service_url}/api/ai/generate/content/",
                f"{self.service_url}/api/ai/analyze/sentiment/",
                f"{self.service_url}/api/ai/optimize/hashtags/",
                f"{self.service_url}/api/ai/schedule/optimal/",
                f"{self.service_url}/api/ai/token/usage/",
                f"{self.service_url}/api/ai/models/status/"
            ],
            'capabilities': [
                'content_generation',
                'sentiment_analysis',
                'hashtag_optimization',
                'optimal_posting_time',
                'token_management',
                'quality_assurance'
            ],
            'version': '1.0.0',
            'status': 'active',
            'registered_at': datetime.now().isoformat()
        }
        
        try:
            # In a real implementation, this would register with a service registry
            # For now, we'll just log the registration
            logger.info(f"Service registered: {self.service_name} at {self.service_url}")
            return registration_data
        except Exception as e:
            logger.error(f"Failed to register service: {str(e)}")
            return {'error': str(e)}
    
    def discover_services(self) -> List[Dict]:
        """Discover other services in the microservices architecture"""
        services = [
            {
                'name': 'user-service',
                'url': 'http://localhost:8001',
                'health_endpoint': 'http://localhost:8001/health/',
                'capabilities': ['user_management', 'authentication']
            },
            {
                'name': 'content-service',
                'url': 'http://localhost:8002',
                'health_endpoint': 'http://localhost:8002/health/',
                'capabilities': ['content_management', 'post_creation']
            },
            {
                'name': 'social-service',
                'url': 'http://localhost:8003',
                'health_endpoint': 'http://localhost:8003/health/',
                'capabilities': ['social_media_integration', 'posting']
            },
            {
                'name': 'analytics-service',
                'url': 'http://localhost:8004',
                'health_endpoint': 'http://localhost:8004/health/',
                'capabilities': ['analytics', 'reporting']
            },
            {
                'name': 'notification-service',
                'url': 'http://localhost:8006',
                'health_endpoint': 'http://localhost:8006/health/',
                'capabilities': ['notifications', 'email_sending']
            }
        ]
        
        return services
    
    def check_service_health(self, service_url: str) -> Dict:
        """Check health of a specific service"""
        try:
            response = requests.get(f"{service_url}/health/", timeout=5)
            if response.status_code == 200:
                return {
                    'service_url': service_url,
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'last_check': datetime.now().isoformat()
                }
            else:
                return {
                    'service_url': service_url,
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}",
                    'last_check': datetime.now().isoformat()
                }
        except requests.exceptions.RequestException as e:
            return {
                'service_url': service_url,
                'status': 'unreachable',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def get_healthy_services(self) -> List[Dict]:
        """Get list of healthy services"""
        services = self.discover_services()
        healthy_services = []
        
        for service in services:
            health_status = self.check_service_health(service['health_endpoint'])
            if health_status['status'] == 'healthy':
                healthy_services.append({
                    **service,
                    'health_status': health_status
                })
        
        return healthy_services

class MonitoringIntegration:
    """Integration with monitoring systems"""
    
    def __init__(self):
        self.metrics_endpoint = None
        self.alerting_endpoint = None
    
    def send_metrics(self, metrics: Dict) -> bool:
        """Send metrics to monitoring system"""
        try:
            # In a real implementation, this would send to Prometheus, DataDog, etc.
            logger.info(f"Sending metrics: {json.dumps(metrics, indent=2)}")
            return True
        except Exception as e:
            logger.error(f"Failed to send metrics: {str(e)}")
            return False
    
    def send_alert(self, alert: Dict) -> bool:
        """Send alert to monitoring system"""
        try:
            # In a real implementation, this would send to PagerDuty, Slack, etc.
            logger.warning(f"Sending alert: {json.dumps(alert, indent=2)}")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
            return False
    
    def get_service_metrics(self) -> Dict:
        """Get current service metrics"""
        from .performance_monitor import performance_monitor
        
        performance_summary = performance_monitor.get_performance_summary()
        
        return {
            'service_name': 'ai-service',
            'timestamp': datetime.now().isoformat(),
            'performance': performance_summary,
            'endpoints': [
                {
                    'name': 'content_generation',
                    'url': '/api/ai/generate/content/',
                    'status': 'active'
                },
                {
                    'name': 'sentiment_analysis',
                    'url': '/api/ai/analyze/sentiment/',
                    'status': 'active'
                },
                {
                    'name': 'hashtag_optimization',
                    'url': '/api/ai/optimize/hashtags/',
                    'status': 'active'
                },
                {
                    'name': 'optimal_posting_time',
                    'url': '/api/ai/schedule/optimal/',
                    'status': 'active'
                },
                {
                    'name': 'token_usage',
                    'url': '/api/ai/token/usage/',
                    'status': 'active'
                },
                {
                    'name': 'models_status',
                    'url': '/api/ai/models/status/',
                    'status': 'active'
                }
            ]
        }

class InterServiceCommunication:
    """Handle communication between microservices"""
    
    def __init__(self):
        self.service_discovery = ServiceDiscovery()
        self.monitoring = MonitoringIntegration()
    
    def call_user_service(self, endpoint: str, data: Dict = None) -> Dict:
        """Call user service endpoint"""
        user_service_url = 'http://localhost:8001'
        
        try:
            url = f"{user_service_url}{endpoint}"
            if data:
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None,
                'status_code': response.status_code
            }
        except Exception as e:
            logger.error(f"Failed to call user service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def call_content_service(self, endpoint: str, data: Dict = None) -> Dict:
        """Call content service endpoint"""
        content_service_url = 'http://localhost:8002'
        
        try:
            url = f"{content_service_url}{endpoint}"
            if data:
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None,
                'status_code': response.status_code
            }
        except Exception as e:
            logger.error(f"Failed to call content service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def call_social_service(self, endpoint: str, data: Dict = None) -> Dict:
        """Call social service endpoint"""
        social_service_url = 'http://localhost:8003'
        
        try:
            url = f"{social_service_url}{endpoint}"
            if data:
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None,
                'status_code': response.status_code
            }
        except Exception as e:
            logger.error(f"Failed to call social service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instances
service_discovery = ServiceDiscovery()
monitoring_integration = MonitoringIntegration()
inter_service_comm = InterServiceCommunication() 