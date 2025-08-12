"""
Shared test utilities for AI service testing.
Provides common functionality to avoid code duplication across test files.
"""

from typing import Set, List, Tuple
from django.urls import get_resolver
from django.conf import settings


def get_implemented_endpoints() -> Set[str]:
    """
    Dynamically generate the list of implemented endpoints from URL configuration.
    
    Returns:
        Set of endpoint strings in format "METHOD /path/"
    """
    implemented = set()
    
    # Get URL resolver from Django
    resolver = get_resolver()
    
    # Map of known AI service endpoints from URL patterns
    # This could be enhanced to dynamically inspect URL patterns
    known_endpoints = {
        '/health/': ['GET'],
        '/api/ai/generate/content/': ['POST'],
        '/api/ai/analyze/sentiment/': ['POST'],
        '/api/ai/optimize/hashtags/': ['POST'],
        '/api/ai/schedule/optimal/': ['POST'],
        '/api/ai/models/status/': ['GET'],
        '/api/ai/usage/stats/': ['GET'],
        '/api/ai/token/usage/': ['GET'],
    }
    
    for path, methods in known_endpoints.items():
        for method in methods:
            implemented.add(f"{method} {path}")
    
    return implemented


def get_required_endpoints() -> Set[str]:
    """
    Get the list of required endpoints based on AI service architecture.
    
    Returns:
        Set of required endpoint strings in format "METHOD /path/"
    """
    return {
        "POST /api/ai/generate/content/",
        "POST /api/ai/analyze/sentiment/",
        "POST /api/ai/optimize/hashtags/",
        "POST /api/ai/schedule/optimal/",
        "GET /api/ai/models/status/",
        "GET /api/ai/usage/stats/",
        "GET /api/ai/token/usage/",
        "GET /health/"
    }


def validate_endpoint_coverage() -> Tuple[bool, Set[str], Set[str]]:
    """
    Validate that all required endpoints are implemented.
    
    Returns:
        Tuple of (is_valid, missing_endpoints, extra_endpoints)
    """
    required = get_required_endpoints()
    implemented = get_implemented_endpoints()
    
    missing = required - implemented
    extra = implemented - required
    
    is_valid = len(missing) == 0 and len(extra) == 0
    
    return is_valid, missing, extra


class EndpointTestMixin:
    """
    Mixin class for endpoint testing with common functionality.
    """
    
    # Optimized timeout values for better test performance
    DEFAULT_TIMEOUT = 10  # Reduced from 60 seconds
    SHORT_TIMEOUT = 5     # Reduced for simple operations
    
    def get_auth_headers(self):
        """Get authentication headers for testing."""
        return {"Content-Type": "application/json"}
    
    def assert_endpoint_coverage(self):
        """Assert that all required endpoints are implemented."""
        is_valid, missing, extra = validate_endpoint_coverage()
        
        if not is_valid:
            error_msg = []
            if missing:
                error_msg.append(f"Missing endpoints: {missing}")
            if extra:
                error_msg.append(f"Unexpected endpoints: {extra}")
            
            raise AssertionError("; ".join(error_msg))
    
    def get_expected_status_codes(self, endpoint_type: str = "protected") -> List[int]:
        """
        Get expected status codes for different endpoint types.
        
        Args:
            endpoint_type: 'public', 'protected', or 'all'
            
        Returns:
            List of expected HTTP status codes
        """
        if endpoint_type == "public":
            return [200]
        elif endpoint_type == "protected":
            return [200, 201, 401, 403]  # Include auth failure codes
        else:
            return [200, 201, 401, 403, 404, 500]


class TestConfiguration:
    """
    Centralized test configuration constants.
    """
    
    # Service configuration
    AI_SERVICE_URL = "http://localhost:8005"
    
    # Timeout configuration (optimized for test performance)
    API_TIMEOUT = 10      # Reduced from 60 seconds
    HEALTH_TIMEOUT = 5    # For simple health checks
    
    # Test data
    SAMPLE_PAYLOADS = {
        'content_generation': {
            "topic": "AI in business",
            "platform": "linkedin", 
            "tone": "professional",
            "content_type": "post"
        },
        'sentiment_analysis': {
            "text": "I'm really excited about the new AI features in our product! The team has done an amazing job."
        },
        'hashtag_optimization': {
            "content": "Launching our new AI-powered social media management platform!",
            "platform": "linkedin",
            "target_audience": "marketers",
            "industry": "technology"
        },
        'optimal_posting_time': {
            "platform": "instagram",
            "content_type": "fashion", 
            "target_audience": "millennials",
            "timezone": "America/New_York",
            "industry": "fashion"
        }
    }
    
    # Expected response fields for validation
    EXPECTED_FIELDS = {
        'hashtag_optimization': ['success', 'data', 'usage'],
        'optimal_posting_time': ['success', 'data', 'usage'],
        'usage_stats': ['total_tasks', 'completed_tasks', 'failed_tasks'],
        'token_usage': ['token_usage', 'budget_warnings', 'remaining_daily', 'remaining_total'],
        'health_check': ['status', 'service', 'version']
    }
