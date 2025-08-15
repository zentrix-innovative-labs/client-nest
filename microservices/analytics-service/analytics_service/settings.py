import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-analytics-service-key')

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
    
    # Local apps
    'performance',
    'ai_usage',
    'reports',
    'metrics',
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

ROOT_URLCONF = 'analytics_service.urls'

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

WSGI_APPLICATION = 'analytics_service.wsgi.application'

# Database - Using TimescaleDB for time-series analytics data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='analytics_service_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5434'),
        'OPTIONS': {
            'options': '-c search_path=public,timescaledb'
        }
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
    'AI_SERVICE': config('AI_SERVICE_URL', default='http://localhost:8005'),
    'NOTIFICATION_SERVICE': config('NOTIFICATION_SERVICE_URL', default='http://localhost:8006'),
    'QUEUE_SERVICE': config('QUEUE_SERVICE_URL', default='http://localhost:8007'),
    'SECURITY_SERVICE': config('SECURITY_SERVICE_URL', default='http://localhost:8008'),
    'FILE_SERVICE': config('FILE_SERVICE_URL', default='http://localhost:8009'),
    'WEBHOOK_SERVICE': config('WEBHOOK_SERVICE_URL', default='http://localhost:8010'),
}

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/2')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Analytics Configuration
ANALYTICS_CONFIG = {
    'RETENTION_DAYS': config('ANALYTICS_RETENTION_DAYS', default=365, cast=int),
    'AGGREGATION_INTERVALS': ['hour', 'day', 'week', 'month'],
    'METRICS_BATCH_SIZE': config('METRICS_BATCH_SIZE', default=1000, cast=int),
    'REAL_TIME_THRESHOLD_MINUTES': config('REAL_TIME_THRESHOLD_MINUTES', default=5, cast=int),
}

# External Analytics APIs
EXTERNAL_ANALYTICS = {
    'GOOGLE_ANALYTICS': {
        'MEASUREMENT_ID': config('GA_MEASUREMENT_ID', default=''),
        'API_SECRET': config('GA_API_SECRET', default=''),
    },
    'FACEBOOK_INSIGHTS': {
        'ACCESS_TOKEN': config('FB_INSIGHTS_TOKEN', default=''),
    },
    'TWITTER_ANALYTICS': {
        'BEARER_TOKEN': config('TWITTER_ANALYTICS_BEARER_TOKEN', default=''),
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
            'filename': 'analytics_service.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}