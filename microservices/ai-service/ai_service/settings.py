import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

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
    'django_celery_results',
    
    # Local apps
    'content_generation',
    'sentiment_analysis',
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
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
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
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')

# Service Communication
SERVICE_URLS = {
    'USER_SERVICE': os.environ.get('USER_SERVICE_URL', 'http://localhost:8001'),
    'CONTENT_SERVICE': os.environ.get('CONTENT_SERVICE_URL', 'http://localhost:8002'),
    'SOCIAL_SERVICE': os.environ.get('SOCIAL_SERVICE_URL', 'http://localhost:8003'),
    'ANALYTICS_SERVICE': os.environ.get('ANALYTICS_SERVICE_URL', 'http://localhost:8004'),
    'NOTIFICATION_SERVICE': os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:8006'),
    'QUEUE_SERVICE': os.environ.get('QUEUE_SERVICE_URL', 'http://localhost:8007'),
    'SECURITY_SERVICE': os.environ.get('SECURITY_SERVICE_URL', 'http://localhost:8008'),
    'FILE_SERVICE': os.environ.get('FILE_SERVICE_URL', 'http://localhost:8009'),
    'WEBHOOK_SERVICE': os.environ.get('WEBHOOK_SERVICE_URL', 'http://localhost:8010'),
}

# AI Model Configuration
AI_MODELS = {
    'DEEPSEEK': {
        'API_KEY': os.environ.get('DEEPSEEK_API_KEY', ''),
        'BASE_URL': os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
        'MODEL_NAME': os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat'),
        'MAX_TOKENS': int(os.environ.get('DEEPSEEK_MAX_TOKENS', '4000')),
        'TEMPERATURE': float(os.environ.get('DEEPSEEK_TEMPERATURE', '0.7')),
    },
    'OPENAI': {
        'API_KEY': os.environ.get('OPENAI_API_KEY', ''),
        'MODEL_NAME': os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
        'MAX_TOKENS': int(os.environ.get('OPENAI_MAX_TOKENS', '4000')),
        'TEMPERATURE': float(os.environ.get('OPENAI_TEMPERATURE', '0.7')),
    },
    'ANTHROPIC': {
        'API_KEY': os.environ.get('ANTHROPIC_API_KEY', ''),
        'MODEL_NAME': os.environ.get('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
        'MAX_TOKENS': int(os.environ.get('ANTHROPIC_MAX_TOKENS', '4000')),
        'TEMPERATURE': float(os.environ.get('ANTHROPIC_TEMPERATURE', '0.7')),
    },
}

# DeepSeek Pricing Configuration
DEEPSEEK_PRICING = {
    "content_generation": 0.01,  # Example: $0.01 per request
    "sentiment_analysis": 0.005,  # Example: $0.005 per request
    "prompt": 0.001,  # Cost per 1000 prompt tokens
    "completion": 0.002,  # Cost per 1000 completion tokens
    # Add other endpoints as needed
}

# Token Optimization Settings (for 1M token budget)
TOKEN_BUDGET = {
    'TOTAL_TOKENS': int(os.environ.get('TOKEN_BUDGET_TOTAL', '1000000')),  # 1M tokens
    'DAILY_LIMIT': int(os.environ.get('TOKEN_BUDGET_DAILY', '50000')),      # 50K tokens per day
    'REQUEST_LIMIT': int(os.environ.get('TOKEN_BUDGET_REQUEST_LIMIT', '2000')),      # Max tokens per request
    'WARNING_THRESHOLD': float(os.environ.get('TOKEN_WARNING_THRESHOLD', '0.8')),   # Warn at 80% usage
    'EMERGENCY_THRESHOLD': float(os.environ.get('TOKEN_EMERGENCY_THRESHOLD', '0.95')), # Stop at 95% usage
}

# Content Generation Settings
CONTENT_GENERATION = {
    'DEFAULT_MODEL': os.environ.get('DEFAULT_AI_MODEL', 'DEEPSEEK'),
    'FALLBACK_MODEL': os.environ.get('FALLBACK_AI_MODEL', 'OPENAI'),
    'MAX_RETRIES': int(os.environ.get('AI_MAX_RETRIES', '3')),
    'TIMEOUT_SECONDS': int(os.environ.get('AI_TIMEOUT_SECONDS', '30')),
    'RATE_LIMIT_PER_MINUTE': int(os.environ.get('AI_RATE_LIMIT_PER_MINUTE', '60')),
    # Token optimization settings
    'MAX_TOKENS_PER_REQUEST': int(os.environ.get('AI_MAX_TOKENS_PER_REQUEST', '1500')),  # Reduced from 800
    'OPTIMIZE_PROMPTS': True,
    'USE_SHORT_PROMPTS': True,
    'CACHE_RESPONSES': True,
}

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/3')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Django Celery Results
CELERY_CACHE_BACKEND = 'default'

# Additional Environment Variables
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
SERVICE_NAME = 'ai-service'
SERVICE_VERSION = '1.0.0'
SERVICE_PORT = 8005

# Security Settings
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': 'ai_service.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'content_generation': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'common': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}

# ===== CONFIGURATION VALIDATION =====
def validate_configuration():
    """Validate that all required configuration is present"""
    required_vars = [
        'SECRET_KEY',
        'DB_NAME',
        'DB_USER', 
        'DB_PASSWORD',
        'DEEPSEEK_API_KEY',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var, ''):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate configuration on startup
validate_configuration()