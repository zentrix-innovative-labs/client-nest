import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-file-service-key')

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
    'storages',
    
    # Local apps
    'file_upload',
    'media_processing',
    'storage_management',
    'cdn_integration',
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

ROOT_URLCONF = 'file_service.urls'

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

WSGI_APPLICATION = 'file_service.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='file_service_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5438'),
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

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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
    'AI_SERVICE': config('AI_SERVICE_URL', default='http://localhost:8005'),
    'NOTIFICATION_SERVICE': config('NOTIFICATION_SERVICE_URL', default='http://localhost:8006'),
    'QUEUE_SERVICE': config('QUEUE_SERVICE_URL', default='http://localhost:8007'),
    'SECURITY_SERVICE': config('SECURITY_SERVICE_URL', default='http://localhost:8008'),
    'WEBHOOK_SERVICE': config('WEBHOOK_SERVICE_URL', default='http://localhost:8010'),
}

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='clientnest-files')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'

# Use S3 for file storage in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'

# File Upload Configuration
FILE_UPLOAD_CONFIG = {
    'MAX_FILE_SIZE': config('MAX_FILE_SIZE', default=50 * 1024 * 1024, cast=int),  # 50MB
    'ALLOWED_IMAGE_TYPES': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
    'ALLOWED_VIDEO_TYPES': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
    'ALLOWED_DOCUMENT_TYPES': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
    'ALLOWED_AUDIO_TYPES': ['mp3', 'wav', 'ogg', 'aac'],
    'THUMBNAIL_SIZES': {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (800, 600),
    },
    'VIDEO_COMPRESSION_QUALITY': config('VIDEO_COMPRESSION_QUALITY', default=23, cast=int),
    'IMAGE_COMPRESSION_QUALITY': config('IMAGE_COMPRESSION_QUALITY', default=85, cast=int),
}

# CDN Configuration
CDN_CONFIG = {
    'CLOUDFLARE': {
        'ZONE_ID': config('CLOUDFLARE_ZONE_ID', default=''),
        'API_TOKEN': config('CLOUDFLARE_API_TOKEN', default=''),
        'DOMAIN': config('CLOUDFLARE_DOMAIN', default=''),
    },
    'CLOUDFRONT': {
        'DISTRIBUTION_ID': config('CLOUDFRONT_DISTRIBUTION_ID', default=''),
        'DOMAIN': config('CLOUDFRONT_DOMAIN', default=''),
    },
}

# Media Processing Configuration
MEDIA_PROCESSING = {
    'FFMPEG_PATH': config('FFMPEG_PATH', default='/usr/bin/ffmpeg'),
    'IMAGEMAGICK_PATH': config('IMAGEMAGICK_PATH', default='/usr/bin/convert'),
    'ENABLE_ASYNC_PROCESSING': config('ENABLE_ASYNC_PROCESSING', default=True, cast=bool),
    'PROCESSING_TIMEOUT': config('PROCESSING_TIMEOUT', default=300, cast=int),  # 5 minutes
    'WATERMARK_ENABLED': config('WATERMARK_ENABLED', default=False, cast=bool),
    'WATERMARK_PATH': config('WATERMARK_PATH', default=''),
}

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/6')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    'cleanup-temp-files': {
        'task': 'file_upload.tasks.cleanup_temp_files',
        'schedule': 3600.0,  # Run every hour
    },
    'generate-usage-reports': {
        'task': 'storage_management.tasks.generate_usage_reports',
        'schedule': 86400.0,  # Run daily
    },
}

# Security Configuration for File Uploads
FILE_SECURITY = {
    'SCAN_UPLOADS': config('SCAN_UPLOADS', default=True, cast=bool),
    'VIRUS_SCANNER_API': config('VIRUS_SCANNER_API', default=''),
    'QUARANTINE_SUSPICIOUS_FILES': config('QUARANTINE_SUSPICIOUS_FILES', default=True, cast=bool),
    'ENCRYPT_SENSITIVE_FILES': config('ENCRYPT_SENSITIVE_FILES', default=False, cast=bool),
    'FILE_ACCESS_LOGS': config('FILE_ACCESS_LOGS', default=True, cast=bool),
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'file_service.log',
        },
        'upload_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'file_uploads.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'file_upload': {
            'handlers': ['upload_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}