"""
Performance Monitoring System for AI Service
Monitors response times, token usage, error rates, and service health
"""

import time
import logging
import statistics
import functools
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from django.conf import settings
import threading

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_time: float
    token_usage: int
    error_occurred: bool
    timestamp: datetime
    endpoint: str
    user_id: Optional[str] = None

class PerformanceMonitor:
    """Performance monitoring system"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.error_count = 0
        self.total_requests = 0
        self.start_time = datetime.now()
        self._lock = threading.Lock()
    
    def record_request(self, response_time: float, token_usage: int, 
                      error_occurred: bool, endpoint: str, user_id: Optional[str] = None):
        """Record a request's performance metrics"""
        metric = PerformanceMetrics(
            response_time=response_time,
            token_usage=token_usage,
            error_occurred=error_occurred,
            timestamp=datetime.now(),
            endpoint=endpoint,
            user_id=user_id
        )
        with self._lock:
            self.metrics.append(metric)
            self.total_requests += 1
            if error_occurred:
                self.error_count += 1
        # Log performance data
        logger.info(f"Performance: {endpoint} - {response_time:.2f}s, {token_usage} tokens, error: {error_occurred}")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        with self._lock:
            metrics_copy = list(self.metrics)
            error_count = self.error_count
            total_requests = self.total_requests
            start_time = self.start_time
        if not metrics_copy:
            return {
                'total_requests': 0,
                'error_rate': 0.0,
                'avg_response_time': 0.0,
                'total_token_usage': 0,
                'uptime': 0.0
            }
        response_times = [m.response_time for m in metrics_copy]
        token_usages = [m.token_usage for m in metrics_copy]
        return {
            'total_requests': total_requests,
            'error_rate': (error_count / total_requests) * 100 if total_requests > 0 else 0,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'total_token_usage': sum(token_usages),
            'avg_token_usage': statistics.mean(token_usages),
            'uptime': (datetime.now() - start_time).total_seconds(),
            'requests_per_minute': self._calculate_rpm()
        }
    
    def get_endpoint_performance(self, endpoint: str) -> Dict:
        """Get performance metrics for specific endpoint"""
        with self._lock:
            endpoint_metrics = [m for m in self.metrics if m.endpoint == endpoint]
        if not endpoint_metrics:
            return {'endpoint': endpoint, 'requests': 0}
        response_times = [m.response_time for m in endpoint_metrics]
        token_usages = [m.token_usage for m in endpoint_metrics]
        errors = [m for m in endpoint_metrics if m.error_occurred]
        return {
            'endpoint': endpoint,
            'requests': len(endpoint_metrics),
            'avg_response_time': statistics.mean(response_times),
            'error_rate': (len(errors) / len(endpoint_metrics)) * 100,
            'total_token_usage': sum(token_usages),
            'avg_token_usage': statistics.mean(token_usages)
        }
    
    def _calculate_rpm(self) -> float:
        with self._lock:
            total_requests = self.total_requests
            start_time = self.start_time
        if not total_requests:
            return 0.0
        time_diff = datetime.now() - start_time
        minutes = time_diff.total_seconds() / 60
        return total_requests / minutes if minutes > 0 else 0.0
    
    def get_recent_metrics(self, minutes: int = 10) -> List[PerformanceMetrics]:
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self._lock:
            return [m for m in self.metrics if m.timestamp > cutoff_time]
    
    def clear_old_metrics(self, hours: int = 24):
        cutoff_time = datetime.now() - timedelta(hours=hours)
        with self._lock:
            self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        error_occurred = False
        token_usage = 0
        
        try:
            result = func(*args, **kwargs)
            
            # Extract token usage if available
            if isinstance(result, dict) and 'usage' in result:
                usage = result['usage']
                token_usage = usage.get('prompt_tokens', 0) + usage.get('completion_tokens', 0)
            
            return result
            
        except Exception as e:
            error_occurred = True
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
        
        finally:
            response_time = time.time() - start_time
            performance_monitor.record_request(
                response_time=response_time,
                token_usage=token_usage,
                error_occurred=error_occurred,
                endpoint=func.__name__
            )
    
    return wrapper

class HealthCheck:
    """Health check system"""
    
    @staticmethod
    def check_service_health() -> Dict:
        """Check overall service health"""
        performance_summary = performance_monitor.get_performance_summary()
        
        # Define health thresholds
        error_rate_threshold = 5.0  # 5% error rate
        response_time_threshold = 3.0  # 3 seconds
        uptime_threshold = 3600  # 1 hour minimum uptime
        
        is_healthy = (
            performance_summary['error_rate'] < error_rate_threshold and
            performance_summary['avg_response_time'] < response_time_threshold and
            performance_summary['uptime'] > uptime_threshold
        )
        
        return {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'error_rate': performance_summary['error_rate'],
            'avg_response_time': performance_summary['avg_response_time'],
            'uptime': performance_summary['uptime'],
            'total_requests': performance_summary['total_requests'],
            'requests_per_minute': performance_summary['requests_per_minute']
        }
    
    @staticmethod
    def check_ai_model_health() -> Dict:
        """Check AI model health"""
        # This would typically check if the AI model is responding
        # For now, return a mock status
        return {
            'status': 'healthy',
            'model': 'deepseek-chat',
            'last_check': datetime.now().isoformat(),
            'response_time': 0.5
        }

class AlertSystem:
    """Alert system for performance issues"""
    
    @staticmethod
    def check_alerts() -> List[Dict]:
        """Check for performance alerts"""
        alerts = []
        performance_summary = performance_monitor.get_performance_summary()
        
        # High error rate alert
        if performance_summary['error_rate'] > 10.0:
            alerts.append({
                'type': 'high_error_rate',
                'message': f"Error rate is {performance_summary['error_rate']:.1f}%",
                'severity': 'high'
            })
        
        # Slow response time alert
        if performance_summary['avg_response_time'] > 5.0:
            alerts.append({
                'type': 'slow_response_time',
                'message': f"Average response time is {performance_summary['avg_response_time']:.2f}s",
                'severity': 'medium'
            })
        
        # High token usage alert
        if performance_summary['total_token_usage'] > 10000:
            alerts.append({
                'type': 'high_token_usage',
                'message': f"High token usage: {performance_summary['total_token_usage']} tokens",
                'severity': 'medium'
            })
        
        return alerts 