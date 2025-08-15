import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-webhook-service-key')

# SECURITY WARNING: don't run with debug turned on in production!
# Default to False for security - must explicitly set DEBUG=true in environment for development
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
    'celery',
    'django_ratelimit',
    
    # Local apps
    'webhook_handlers',
    'event_processing',
    'external_integrations',
    'notification_delivery',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
]

ROOT_URLCONF = 'webhook_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'webhook_service.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='webhook_service_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5439'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'webhook': '10000/hour',
    }
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Service Communication
SERVICE_URLS = {
    'USER_SERVICE': config('USER_SERVICE_URL', default='http://localhost:8001'),
    'CONTENT_SERVICE': config('CONTENT_SERVICE_URL', default='http://localhost:8002'),
    'SOCIAL_SERVICE': config('SOCIAL_SERVICE_URL', default='http://localhost:8003'),
    'ANALYTICS_SERVICE': config('ANALYTICS_SERVICE_URL', default='http://localhost:8004'),
    'AI_SERVICE': config('AI_SERVICE_URL', default='http://localhost:8005'),
    'NOTIFICATION_SERVICE': config('NOTIFICATION_SERVICE_URL', default='http://localhost:8006'),
    'QUEUE_SERVICE': config('QUEUE_SERVICE_URL', default='http://localhost:8007'),
    'SECURITY_SERVICE': config('SECURITY_SERVICE_URL', default='http://localhost:8008'),
    'FILE_SERVICE': config('FILE_SERVICE_URL', default='http://localhost:8009'),
}

# Webhook Configuration
WEBHOOK_CONFIG = {
    'MAX_RETRIES': config('WEBHOOK_MAX_RETRIES', default=3, cast=int),
    'RETRY_DELAY': config('WEBHOOK_RETRY_DELAY', default=60, cast=int),  # seconds
    'TIMEOUT': config('WEBHOOK_TIMEOUT', default=30, cast=int),  # seconds
    'VERIFY_SSL': config('WEBHOOK_VERIFY_SSL', default=True, cast=bool),
    'MAX_PAYLOAD_SIZE': config('WEBHOOK_MAX_PAYLOAD_SIZE', default=1024*1024, cast=int),  # 1MB
    'SIGNATURE_HEADER': config('WEBHOOK_SIGNATURE_HEADER', default='X-Webhook-Signature'),
    'TIMESTAMP_HEADER': config('WEBHOOK_TIMESTAMP_HEADER', default='X-Webhook-Timestamp'),
    'EVENT_TYPE_HEADER': config('WEBHOOK_EVENT_TYPE_HEADER', default='X-Event-Type'),
}

# External Integration Settings
EXTERNAL_INTEGRATIONS = {
    'SLACK': {
        'WEBHOOK_URL': config('SLACK_WEBHOOK_URL', default=''),
        'BOT_TOKEN': config('SLACK_BOT_TOKEN', default=''),
        'SIGNING_SECRET': config('SLACK_SIGNING_SECRET', default=''),
    },
    'DISCORD': {
        'WEBHOOK_URL': config('DISCORD_WEBHOOK_URL', default=''),
        'BOT_TOKEN': config('DISCORD_BOT_TOKEN', default=''),
    },
    'TEAMS': {
        'WEBHOOK_URL': config('TEAMS_WEBHOOK_URL', default=''),
    },
    'ZAPIER': {
        'API_KEY': config('ZAPIER_API_KEY', default=''),
        'WEBHOOK_URL': config('ZAPIER_WEBHOOK_URL', default=''),
    },
    'IFTTT': {
        'MAKER_KEY': config('IFTTT_MAKER_KEY', default=''),
        'WEBHOOK_URL': config('IFTTT_WEBHOOK_URL', default=''),
    },
    'GITHUB': {
        'WEBHOOK_SECRET': config('GITHUB_WEBHOOK_SECRET', default=''),
        'ACCESS_TOKEN': config('GITHUB_ACCESS_TOKEN', default=''),
    },
    'STRIPE': {
        'WEBHOOK_SECRET': config('STRIPE_WEBHOOK_SECRET', default=''),
        'API_KEY': config('STRIPE_API_KEY', default=''),
    },
    'PAYPAL': {
        'WEBHOOK_ID': config('PAYPAL_WEBHOOK_ID', default=''),
        'CLIENT_ID': config('PAYPAL_CLIENT_ID', default=''),
        'CLIENT_SECRET': config('PAYPAL_CLIENT_SECRET', default=''),
    },
}

# Event Processing Configuration
EVENT_PROCESSING = {
    'BATCH_SIZE': config('EVENT_BATCH_SIZE', default=100, cast=int),
    'PROCESSING_INTERVAL': config('EVENT_PROCESSING_INTERVAL', default=5, cast=int),  # seconds
    'MAX_QUEUE_SIZE': config('EVENT_MAX_QUEUE_SIZE', default=10000, cast=int),
    'DEAD_LETTER_QUEUE_ENABLED': config('DEAD_LETTER_QUEUE_ENABLED', default=True, cast=bool),
    'EVENT_RETENTION_DAYS': config('EVENT_RETENTION_DAYS', default=30, cast=int),
    'ENABLE_EVENT_REPLAY': config('ENABLE_EVENT_REPLAY', default=True, cast=bool),
}

# Rate Limiting Configuration
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Notification Delivery Settings
NOTIFICATION_DELIVERY = {
    'EMAIL': {
        'SMTP_HOST': config('SMTP_HOST', default='localhost'),
        'SMTP_PORT': config('SMTP_PORT', default=587, cast=int),
        'SMTP_USER': config('SMTP_USER', default=''),
        'SMTP_PASSWORD': config('SMTP_PASSWORD', default=''),
        'USE_TLS': config('SMTP_USE_TLS', default=True, cast=bool),
        'FROM_EMAIL': config('FROM_EMAIL', default='noreply@clientnest.com'),
    },
    'SMS': {
        'TWILIO_ACCOUNT_SID': config('TWILIO_ACCOUNT_SID', default=''),
        'TWILIO_AUTH_TOKEN': config('TWILIO_AUTH_TOKEN', default=''),
        'TWILIO_PHONE_NUMBER': config('TWILIO_PHONE_NUMBER', default=''),
    },
    'PUSH': {
        'FCM_SERVER_KEY': config('FCM_SERVER_KEY', default=''),
        'APNS_CERTIFICATE': config('APNS_CERTIFICATE', default=''),
        'APNS_KEY_ID': config('APNS_KEY_ID', default=''),
        'APNS_TEAM_ID': config('APNS_TEAM_ID', default=''),
    },
}

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/7')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    'process-webhook-queue': {
        'task': 'webhook_handlers.tasks.process_webhook_queue',
        'schedule': 10.0,  # Run every 10 seconds
    },
    'cleanup-old-events': {
        'task': 'event_processing.tasks.cleanup_old_events',
        'schedule': 86400.0,  # Run daily
    },
    'retry-failed-webhooks': {
        'task': 'webhook_handlers.tasks.retry_failed_webhooks',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'send-delivery-reports': {
        'task': 'notification_delivery.tasks.send_delivery_reports',
        'schedule': 3600.0,  # Run hourly
    },
}

# Security Configuration
WEBHOOK_SECURITY = {
    'REQUIRE_SIGNATURE': config('WEBHOOK_REQUIRE_SIGNATURE', default=True, cast=bool),
    'SIGNATURE_ALGORITHM': config('WEBHOOK_SIGNATURE_ALGORITHM', default='sha256'),
    'TIMESTAMP_TOLERANCE': config('WEBHOOK_TIMESTAMP_TOLERANCE', default=300, cast=int),  # 5 minutes
    'IP_WHITELIST_ENABLED': config('WEBHOOK_IP_WHITELIST_ENABLED', default=False, cast=bool),
    'ALLOWED_IPS': config('WEBHOOK_ALLOWED_IPS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]),
    'RATE_LIMIT_PER_IP': config('WEBHOOK_RATE_LIMIT_PER_IP', default='100/hour'),
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'webhook_service.log',
        },
        'webhook_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'webhook_events.log',
        },
        'delivery_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'notification_delivery.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'webhook_handlers': {
            'handlers': ['webhook_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'notification_delivery': {
            'handlers': ['delivery_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}