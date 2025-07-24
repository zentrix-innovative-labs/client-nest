import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-ai-service-key')

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
    'content_generation',
    'sentiment_analysis',
    'content_optimization',
    'ai_models',
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

ROOT_URLCONF = 'ai_service.urls'

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

WSGI_APPLICATION = 'ai_service.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='ai_service_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5435'),
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
    'PAGE_SIZE': 20,
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
    'NOTIFICATION_SERVICE': config('NOTIFICATION_SERVICE_URL', default='http://localhost:8006'),
    'QUEUE_SERVICE': config('QUEUE_SERVICE_URL', default='http://localhost:8007'),
    'SECURITY_SERVICE': config('SECURITY_SERVICE_URL', default='http://localhost:8008'),
    'FILE_SERVICE': config('FILE_SERVICE_URL', default='http://localhost:8009'),
    'WEBHOOK_SERVICE': config('WEBHOOK_SERVICE_URL', default='http://localhost:8010'),
}

# AI Model Configuration
AI_MODELS = {
    'DEEPSEEK': {
        'API_KEY': config('DEEPSEEK_API_KEY', default=''),
        'BASE_URL': config('DEEPSEEK_BASE_URL', default='https://api.deepseek.com'),
        'MODEL_NAME': config('DEEPSEEK_MODEL', default='deepseek-chat'),
        'MAX_TOKENS': config('DEEPSEEK_MAX_TOKENS', default=4000, cast=int),
        'TEMPERATURE': config('DEEPSEEK_TEMPERATURE', default=0.7, cast=float),
    },
    'OPENAI': {
        'API_KEY': config('OPENAI_API_KEY', default=''),
        'MODEL_NAME': config('OPENAI_MODEL', default='gpt-3.5-turbo'),
        'MAX_TOKENS': config('OPENAI_MAX_TOKENS', default=4000, cast=int),
        'TEMPERATURE': config('OPENAI_TEMPERATURE', default=0.7, cast=float),
    },
    'ANTHROPIC': {
        'API_KEY': config('ANTHROPIC_API_KEY', default=''),
        'MODEL_NAME': config('ANTHROPIC_MODEL', default='claude-3-sonnet-20240229'),
        'MAX_TOKENS': config('ANTHROPIC_MAX_TOKENS', default=4000, cast=int),
        'TEMPERATURE': config('ANTHROPIC_TEMPERATURE', default=0.7, cast=float),
    },
}

# Content Generation Settings
CONTENT_GENERATION = {
    'DEFAULT_MODEL': config('DEFAULT_AI_MODEL', default='DEEPSEEK'),
    'FALLBACK_MODEL': config('FALLBACK_AI_MODEL', default='OPENAI'),
    'MAX_RETRIES': config('AI_MAX_RETRIES', default=3, cast=int),
    'TIMEOUT_SECONDS': config('AI_TIMEOUT_SECONDS', default=30, cast=int),
    'RATE_LIMIT_PER_MINUTE': config('AI_RATE_LIMIT_PER_MINUTE', default=60, cast=int),
}

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/3')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'ai_service.log',
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