from django.conf import settings

# DeepSeek API Configuration
DEEPSEEK_API_KEY = getattr(settings, 'DEEPSEEK_API_KEY', None)
DEEPSEEK_API_BASE_URL = getattr(settings, 'DEEPSEEK_API_BASE_URL', 'https://api.deepseek.com/v1')
DEEPSEEK_API_VERSION = getattr(settings, 'DEEPSEEK_API_VERSION', 'v1')

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    'default': {
        'max_requests': 100,
        'time_window': 60  # seconds
    },
    'content_generation': {
        'max_requests': 50,
        'time_window': 60
    },
    'sentiment_analysis': {
        'max_requests': 200,
        'time_window': 60
    }
}

# Circuit Breaker Configuration
CIRCUIT_BREAKER_CONFIG = {
    'failure_threshold': 5,
    'reset_timeout': 60  # seconds
}

# Tier-based Usage Limits
USAGE_LIMITS = {
    'free': {
        'daily_requests': 50,
        'monthly_requests': 1000,
        'max_tokens': 1000,
        'concurrent_requests': 2,
        'features': ['content_generation', 'sentiment_analysis']
    },
    'basic': {
        'daily_requests': 200,
        'monthly_requests': 5000,
        'max_tokens': 2000,
        'concurrent_requests': 5,
        'features': ['content_generation', 'sentiment_analysis', 'hashtag_generation']
    },
    'premium': {
        'daily_requests': 1000,
        'monthly_requests': 25000,
        'max_tokens': 4000,
        'concurrent_requests': 10,
        'features': ['content_generation', 'sentiment_analysis', 'hashtag_generation',
                    'advanced_analytics']
    },
    'enterprise': {
        'daily_requests': -1,  # Unlimited
        'monthly_requests': -1,  # Unlimited
        'max_tokens': 8000,
        'concurrent_requests': 25,
        'features': ['content_generation', 'sentiment_analysis', 'hashtag_generation',
                    'advanced_analytics', 'custom_models']
    }
}

# Cache Configuration
CACHE_CONFIG = {
    'default_ttl': 1800,  # 30 minutes
    'content_types': {
        'post': 3600,      # 1 hour
        'caption': 3600,    # 1 hour
        'hashtag': 7200,    # 2 hours
        'sentiment': 900    # 15 minutes
    },
    'max_cache_size': 1000  # Maximum number of cached items
}

# Queue Configuration
QUEUE_CONFIG = {
    'default': {
        'retry_delay': 60,  # seconds
        'max_retries': 3,
        'timeout': 300      # 5 minutes
    },
    'priority': {
        'high': {
            'retry_delay': 30,
            'max_retries': 5,
            'timeout': 180
        },
        'low': {
            'retry_delay': 120,
            'max_retries': 2,
            'timeout': 600
        }
    }
}

# Content Policy Configuration
CONTENT_POLICY = {
    'max_prompt_length': 1000,
    'max_text_length': 5000,
    'supported_languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ru', 'zh', 'ja', 'ko'],
    'default_language': 'en',
    'content_filters': {
        'profanity': True,
        'hate_speech': True,
        'adult_content': True,
        'violence': True
    }
}

# Monitoring Configuration
MONITORING_CONFIG = {
    'metrics': {
        'request_duration': True,
        'error_rate': True,
        'usage_by_endpoint': True,
        'usage_by_user': True,
        'cache_hit_rate': True
    },
    'alerts': {
        'error_threshold': 0.05,  # 5% error rate
        'latency_threshold': 2000,  # 2 seconds
        'quota_warning': 0.8       # 80% of quota
    },
    'logging': {
        'request_logging': True,
        'error_logging': True,
        'performance_logging': True
    }
}

# Cost Optimization Configuration
COST_OPTIMIZATION = {
    'off_peak_hours': {
        'start': 22,  # 10 PM
        'end': 6      # 6 AM
    },
    'batch_processing': {
        'enabled': True,
        'max_batch_size': 50,
        'batch_window': 300  # 5 minutes
    },
    'caching_strategy': {
        'cache_similar_requests': True,
        'similarity_threshold': 0.9
    }
}