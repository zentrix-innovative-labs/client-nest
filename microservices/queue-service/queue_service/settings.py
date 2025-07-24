import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-queue-service-key')

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
    'django_rq',
    
    # Local apps
    'task_management',
    'job_scheduling',
    'message_broker',
    'worker_management',
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
]

ROOT_URLCONF = 'queue_service.urls'

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

WSGI_APPLICATION = 'queue_service.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='queue_service_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5436'),
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
    'SECURITY_SERVICE': config('SECURITY_SERVICE_URL', default='http://localhost:8008'),
    'FILE_SERVICE': config('FILE_SERVICE_URL', default='http://localhost:8009'),
    'WEBHOOK_SERVICE': config('WEBHOOK_SERVICE_URL', default='http://localhost:8010'),
}

# Redis Configuration for Queue Management
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/4')

# RQ (Redis Queue) Configuration
RQ_QUEUES = {
    'default': {
        'HOST': config('REDIS_HOST', default='localhost'),
        'PORT': config('REDIS_PORT', default=6379, cast=int),
        'DB': config('REDIS_DB', default=4, cast=int),
        'PASSWORD': config('REDIS_PASSWORD', default=None),
        'DEFAULT_TIMEOUT': config('RQ_DEFAULT_TIMEOUT', default=360, cast=int),
    },
    'high': {
        'HOST': config('REDIS_HOST', default='localhost'),
        'PORT': config('REDIS_PORT', default=6379, cast=int),
        'DB': config('REDIS_DB', default=4, cast=int),
        'PASSWORD': config('REDIS_PASSWORD', default=None),
        'DEFAULT_TIMEOUT': config('RQ_HIGH_TIMEOUT', default=500, cast=int),
    },
    'low': {
        'HOST': config('REDIS_HOST', default='localhost'),
        'PORT': config('REDIS_PORT', default=6379, cast=int),
        'DB': config('REDIS_DB', default=4, cast=int),
        'PASSWORD': config('REDIS_PASSWORD', default=None),
        'DEFAULT_TIMEOUT': config('RQ_LOW_TIMEOUT', default=300, cast=int),
    },
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-tasks': {
        'task': 'task_management.tasks.cleanup_expired_tasks',
        'schedule': 3600.0,  # Run every hour
    },
    'process-scheduled-jobs': {
        'task': 'job_scheduling.tasks.process_scheduled_jobs',
        'schedule': 60.0,  # Run every minute
    },
}

# Queue Configuration
QUEUE_CONFIG = {
    'MAX_RETRIES': config('QUEUE_MAX_RETRIES', default=3, cast=int),
    'RETRY_DELAY': config('QUEUE_RETRY_DELAY', default=60, cast=int),  # seconds
    'TASK_TIMEOUT': config('QUEUE_TASK_TIMEOUT', default=300, cast=int),  # seconds
    'BATCH_SIZE': config('QUEUE_BATCH_SIZE', default=100, cast=int),
    'WORKER_CONCURRENCY': config('QUEUE_WORKER_CONCURRENCY', default=4, cast=int),
}

# Message Broker Configuration
MESSAGE_BROKER = {
    'RABBITMQ_URL': config('RABBITMQ_URL', default='amqp://guest:guest@localhost:5672//'),
    'EXCHANGE_NAME': config('EXCHANGE_NAME', default='clientnest'),
    'ROUTING_KEYS': {
        'user_events': 'user.events',
        'content_events': 'content.events',
        'social_events': 'social.events',
        'analytics_events': 'analytics.events',
        'ai_events': 'ai.events',
        'notification_events': 'notification.events',
    },
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'queue_service.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'rq.worker': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}