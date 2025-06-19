import hashlib
import json
from typing import Dict, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta

def generate_cache_key(prefix: str, data: Dict[str, Any]) -> str:
    """Generate a cache key for AI responses"""
    # Sort dictionary to ensure consistent hash
    sorted_data = json.dumps(data, sort_keys=True)
    # Generate hash
    hash_obj = hashlib.md5(sorted_data.encode())
    return f'ai:{prefix}:{hash_obj.hexdigest()}'

def get_tier_limits(user_tier: str) -> Dict[str, int]:
    """Get AI usage limits based on user tier"""
    tier_limits = {
        'free': {
            'daily_requests': 50,
            'monthly_requests': 1000,
            'max_tokens': 1000,
            'concurrent_requests': 2
        },
        'basic': {
            'daily_requests': 200,
            'monthly_requests': 5000,
            'max_tokens': 2000,
            'concurrent_requests': 5
        },
        'premium': {
            'daily_requests': 1000,
            'monthly_requests': 25000,
            'max_tokens': 4000,
            'concurrent_requests': 10
        },
        'enterprise': {
            'daily_requests': -1,  # Unlimited
            'monthly_requests': -1,  # Unlimited
            'max_tokens': 8000,
            'concurrent_requests': 25
        }
    }
    return tier_limits.get(user_tier, tier_limits['free'])

def check_usage_limits(user_id: int, tier: str) -> bool:
    """Check if user has exceeded their usage limits"""
    tier_limits = get_tier_limits(tier)
    
    # Skip checks for enterprise tier
    if tier == 'enterprise':
        return True
    
    # Check daily requests
    daily_key = f'ai:usage:daily:{user_id}'
    daily_usage = cache.get(daily_key, 0)
    
    if daily_usage >= tier_limits['daily_requests']:
        return False
    
    # Check monthly requests
    monthly_key = f'ai:usage:monthly:{user_id}'
    monthly_usage = cache.get(monthly_key, 0)
    
    if monthly_usage >= tier_limits['monthly_requests']:
        return False
    
    return True

def increment_usage_counters(user_id: int):
    """Increment usage counters for AI requests"""
    # Increment daily counter
    daily_key = f'ai:usage:daily:{user_id}'
    daily_usage = cache.get(daily_key, 0)
    cache.set(daily_key, daily_usage + 1, timeout=86400)  # 24 hours
    
    # Increment monthly counter
    monthly_key = f'ai:usage:monthly:{user_id}'
    monthly_usage = cache.get(monthly_key, 0)
    cache.set(monthly_key, monthly_usage + 1, timeout=2592000)  # 30 days

def get_usage_stats(user_id: int) -> Dict[str, int]:
    """Get current usage statistics for a user"""
    daily_key = f'ai:usage:daily:{user_id}'
    monthly_key = f'ai:usage:monthly:{user_id}'
    
    return {
        'daily_requests': cache.get(daily_key, 0),
        'monthly_requests': cache.get(monthly_key, 0)
    }

def calculate_token_cost(text: str) -> int:
    """Calculate approximate token cost for text"""
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4

def is_off_peak_hours() -> bool:
    """Check if current time is during off-peak hours"""
    current_hour = timezone.now().hour
    # Consider 10 PM - 6 AM as off-peak hours
    return current_hour >= 22 or current_hour < 6

def should_cache_response(content_type: str, platform: str) -> bool:
    """Determine if response should be cached based on content type and platform"""
    # Don't cache personalized or time-sensitive content
    no_cache_types = ['personalized', 'news', 'trending']
    if content_type.lower() in no_cache_types:
        return False
    
    # Don't cache platform-specific dynamic content
    dynamic_platforms = ['twitter', 'instagram']
    if platform.lower() in dynamic_platforms and content_type == 'trending':
        return False
    
    return True

def get_cache_ttl(content_type: str) -> int:
    """Get cache TTL (Time To Live) based on content type"""
    ttl_mapping = {
        'post': 3600,  # 1 hour
        'comment': 1800,  # 30 minutes
        'hashtag': 7200,  # 2 hours
        'caption': 3600,  # 1 hour
        'sentiment': 900,  # 15 minutes
        'default': 1800  # 30 minutes
    }
    return ttl_mapping.get(content_type.lower(), ttl_mapping['default'])