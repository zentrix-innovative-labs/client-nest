import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-security-service-key')

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
    'authentication',
    'authorization',
    'audit_logs',
    'rate_limiting',
    'encryption',
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
    'security_service.middleware.SecurityAuditMiddleware',
    'security_service.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'security_service.urls'

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

WSGI_APPLICATION = 'security_service.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='security_service_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5437'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
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
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=15, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SIGNING_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
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
    'FILE_SERVICE': config('FILE_SERVICE_URL', default='http://localhost:8009'),
    'WEBHOOK_SERVICE': config('WEBHOOK_SERVICE_URL', default='http://localhost:8010'),
}

# Security Configuration
SECURITY_CONFIG = {
    'PASSWORD_RESET_TIMEOUT': config('PASSWORD_RESET_TIMEOUT', default=3600, cast=int),  # 1 hour
    'EMAIL_VERIFICATION_TIMEOUT': config('EMAIL_VERIFICATION_TIMEOUT', default=86400, cast=int),  # 24 hours
    'MAX_LOGIN_ATTEMPTS': config('MAX_LOGIN_ATTEMPTS', default=5, cast=int),
    'ACCOUNT_LOCKOUT_DURATION': config('ACCOUNT_LOCKOUT_DURATION', default=1800, cast=int),  # 30 minutes
    'SESSION_TIMEOUT': config('SESSION_TIMEOUT', default=3600, cast=int),  # 1 hour
    'REQUIRE_2FA': config('REQUIRE_2FA', default=False, cast=bool),
    'ENCRYPTION_KEY': config('ENCRYPTION_KEY', default=''),
    'AUDIT_LOG_RETENTION_DAYS': config('AUDIT_LOG_RETENTION_DAYS', default=90, cast=int),
}

# Rate Limiting Configuration
RATE_LIMITING = {
    'LOGIN_ATTEMPTS': {
        'RATE': '5/5m',  # 5 attempts per 5 minutes
        'BLOCK_DURATION': 900,  # 15 minutes
    },
    'API_CALLS': {
        'RATE': '1000/1h',  # 1000 calls per hour
        'BLOCK_DURATION': 3600,  # 1 hour
    },
    'PASSWORD_RESET': {
        'RATE': '3/1h',  # 3 attempts per hour
        'BLOCK_DURATION': 3600,  # 1 hour
    },
}

# OAuth Configuration
OAUTH_PROVIDERS = {
    'GOOGLE': {
        'CLIENT_ID': config('GOOGLE_OAUTH_CLIENT_ID', default=''),
        'CLIENT_SECRET': config('GOOGLE_OAUTH_CLIENT_SECRET', default=''),
        'REDIRECT_URI': config('GOOGLE_OAUTH_REDIRECT_URI', default=''),
    },
    'FACEBOOK': {
        'CLIENT_ID': config('FACEBOOK_OAUTH_CLIENT_ID', default=''),
        'CLIENT_SECRET': config('FACEBOOK_OAUTH_CLIENT_SECRET', default=''),
        'REDIRECT_URI': config('FACEBOOK_OAUTH_REDIRECT_URI', default=''),
    },
    'GITHUB': {
        'CLIENT_ID': config('GITHUB_OAUTH_CLIENT_ID', default=''),
        'CLIENT_SECRET': config('GITHUB_OAUTH_CLIENT_SECRET', default=''),
        'REDIRECT_URI': config('GITHUB_OAUTH_REDIRECT_URI', default=''),
    },
}

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/5')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '{levelname} {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'security_service.log',
            'formatter': 'security',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'security_audit.log',
            'formatter': 'security',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security_audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}