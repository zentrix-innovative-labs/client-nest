# ClientNest Security Architecture

## Security Overview

ClientNest implements a **defense-in-depth security strategy** with multiple layers of protection:

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Data Protection**: Encryption at rest and in transit
- **API Security**: Rate limiting, input validation, and secure headers
- **Infrastructure Security**: AWS security groups, VPC isolation, and monitoring
- **Compliance**: GDPR, SOC 2, and social media platform requirements

## Security Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SECURITY ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Device   │    │   CDN/WAF       │    │   Load Balancer │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • HTTPS Only    │────│ • DDoS Protection│────│ • SSL Termination│
│ • CSP Headers   │    │ • Rate Limiting  │    │ • Health Checks  │
│ • Secure Cookies│    │ • Geo-blocking   │    │ • Failover       │
│ • Local Storage │    │ • Bot Detection  │    │ • Auto-scaling   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            APPLICATION LAYER                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Frontend      │   API Gateway   │   Auth Service  │    Backend Services     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • JWT Storage   │ • Request       │ • OAuth 2.0     │ • Service-to-Service    │
│ • XSS Protection│   Validation    │ • JWT Tokens    │   Authentication        │
│ • CSRF Tokens   │ • Rate Limiting │ • MFA Support   │ • Input Validation      │
│ • Secure Headers│ • CORS Policy   │ • Session Mgmt  │ • Output Encoding       │
│ • Content Policy│ • API Versioning│ • Password Hash │ • SQL Injection Prevent │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                        │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Database      │   File Storage  │   Cache Layer   │    External APIs        │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Encryption    │ • S3 Encryption │ • Redis Auth    │ • API Key Management    │
│ • Access Control│ • IAM Policies  │ • Memory Limits │ • Rate Limiting         │
│ • Audit Logging │ • Versioning    │ • TTL Policies  │ • Request Signing       │
│ • Backup Encrypt│ • Lifecycle     │ • Secure Config │ • Response Validation   │
│ • Network Isolat│ • Access Logs   │ • Connection    │ • Error Handling        │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MONITORING & COMPLIANCE                                │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Logging       │   Monitoring    │   Alerting      │    Compliance           │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Centralized   │ • Security      │ • Threat        │ • GDPR Compliance       │
│   Logging       │   Metrics       │   Detection     │ • Data Retention        │
│ • Log Encryption│ • Anomaly       │ • Incident      │ • Privacy Controls      │
│ • Access Control│   Detection     │   Response      │ • Audit Trails          │
│ • Retention     │ • Performance   │ • Escalation    │ • Regular Assessments   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## Authentication & Authorization

### JWT-Based Authentication

```python
# backend/authentication/jwt_handler.py
import jwt
import bcrypt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed

class JWTHandler:
    @staticmethod
    def generate_tokens(user):
        """Generate access and refresh tokens for user"""
        now = datetime.utcnow()
        
        # Access token (15 minutes)
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'team_id': user.current_team_id,
            'role': user.role,
            'permissions': user.get_permissions(),
            'iat': now,
            'exp': now + timedelta(minutes=15),
            'type': 'access'
        }
        
        # Refresh token (7 days)
        refresh_payload = {
            'user_id': user.id,
            'iat': now,
            'exp': now + timedelta(days=7),
            'type': 'refresh'
        }
        
        access_token = jwt.encode(
            access_payload, 
            settings.JWT_SECRET_KEY, 
            algorithm='HS256'
        )
        
        refresh_token = jwt.encode(
            refresh_payload, 
            settings.JWT_REFRESH_SECRET_KEY, 
            algorithm='HS256'
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 900  # 15 minutes
        }
    
    @staticmethod
    def verify_token(token, token_type='access'):
        """Verify and decode JWT token"""
        try:
            secret_key = (
                settings.JWT_SECRET_KEY if token_type == 'access' 
                else settings.JWT_REFRESH_SECRET_KEY
            )
            
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=['HS256']
            )
            
            if payload.get('type') != token_type:
                raise AuthenticationFailed('Invalid token type')
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Generate new access token from refresh token"""
        payload = JWTHandler.verify_token(refresh_token, 'refresh')
        
        try:
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                raise AuthenticationFailed('User account is disabled')
            
            return JWTHandler.generate_tokens(user)
            
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

# Custom JWT Authentication Middleware
class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                payload = JWTHandler.verify_token(token)
                request.user_id = payload['user_id']
                request.team_id = payload['team_id']
                request.user_role = payload['role']
                request.user_permissions = payload['permissions']
                
            except AuthenticationFailed:
                # Token invalid, continue without authentication
                pass
        
        response = self.get_response(request)
        return response
```

### Role-Based Access Control (RBAC)

```python
# backend/authentication/permissions.py
from enum import Enum
from functools import wraps
from django.http import JsonResponse
from rest_framework import status

class Role(Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    MANAGER = 'manager'
    MEMBER = 'member'
    VIEWER = 'viewer'

class Permission(Enum):
    # User Management
    CREATE_USER = 'create:user'
    READ_USER = 'read:user'
    UPDATE_USER = 'update:user'
    DELETE_USER = 'delete:user'
    
    # Team Management
    CREATE_TEAM = 'create:team'
    READ_TEAM = 'read:team'
    UPDATE_TEAM = 'update:team'
    DELETE_TEAM = 'delete:team'
    INVITE_MEMBER = 'invite:member'
    
    # Social Media
    CREATE_POST = 'create:post'
    READ_POST = 'read:post'
    UPDATE_POST = 'update:post'
    DELETE_POST = 'delete:post'
    SCHEDULE_POST = 'schedule:post'
    
    # Comments
    READ_COMMENT = 'read:comment'
    RESPOND_COMMENT = 'respond:comment'
    MODERATE_COMMENT = 'moderate:comment'
    
    # AI Features
    USE_AI_CONTENT = 'use:ai_content'
    USE_AI_ANALYSIS = 'use:ai_analysis'
    CONFIGURE_AI = 'configure:ai'
    
    # Analytics
    READ_ANALYTICS = 'read:analytics'
    EXPORT_DATA = 'export:data'
    
    # Billing
    READ_BILLING = 'read:billing'
    UPDATE_BILLING = 'update:billing'

# Role-Permission Mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [
        # All permissions
        *[perm.value for perm in Permission]
    ],
    Role.ADMIN: [
        Permission.CREATE_USER.value,
        Permission.READ_USER.value,
        Permission.UPDATE_USER.value,
        Permission.READ_TEAM.value,
        Permission.UPDATE_TEAM.value,
        Permission.INVITE_MEMBER.value,
        Permission.CREATE_POST.value,
        Permission.READ_POST.value,
        Permission.UPDATE_POST.value,
        Permission.DELETE_POST.value,
        Permission.SCHEDULE_POST.value,
        Permission.READ_COMMENT.value,
        Permission.RESPOND_COMMENT.value,
        Permission.MODERATE_COMMENT.value,
        Permission.USE_AI_CONTENT.value,
        Permission.USE_AI_ANALYSIS.value,
        Permission.CONFIGURE_AI.value,
        Permission.READ_ANALYTICS.value,
        Permission.EXPORT_DATA.value,
        Permission.READ_BILLING.value,
    ],
    Role.MANAGER: [
        Permission.READ_USER.value,
        Permission.READ_TEAM.value,
        Permission.CREATE_POST.value,
        Permission.READ_POST.value,
        Permission.UPDATE_POST.value,
        Permission.SCHEDULE_POST.value,
        Permission.READ_COMMENT.value,
        Permission.RESPOND_COMMENT.value,
        Permission.MODERATE_COMMENT.value,
        Permission.USE_AI_CONTENT.value,
        Permission.USE_AI_ANALYSIS.value,
        Permission.READ_ANALYTICS.value,
    ],
    Role.MEMBER: [
        Permission.READ_USER.value,
        Permission.READ_TEAM.value,
        Permission.CREATE_POST.value,
        Permission.READ_POST.value,
        Permission.UPDATE_POST.value,
        Permission.READ_COMMENT.value,
        Permission.RESPOND_COMMENT.value,
        Permission.USE_AI_CONTENT.value,
        Permission.READ_ANALYTICS.value,
    ],
    Role.VIEWER: [
        Permission.READ_USER.value,
        Permission.READ_TEAM.value,
        Permission.READ_POST.value,
        Permission.READ_COMMENT.value,
        Permission.READ_ANALYTICS.value,
    ],
}

def require_permission(permission):
    """Decorator to check if user has required permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not hasattr(request, 'user_permissions'):
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check if user has required permission
            if permission not in request.user_permissions:
                return JsonResponse(
                    {'error': 'Insufficient permissions'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role):
    """Decorator to check if user has required role or higher"""
    role_hierarchy = {
        Role.VIEWER: 1,
        Role.MEMBER: 2,
        Role.MANAGER: 3,
        Role.ADMIN: 4,
        Role.OWNER: 5,
    }
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user_role'):
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_role = Role(request.user_role)
            if role_hierarchy[user_role] < role_hierarchy[required_role]:
                return JsonResponse(
                    {'error': 'Insufficient role'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage Examples:
# @require_permission(Permission.CREATE_POST.value)
# def create_post(request):
#     pass
#
# @require_role(Role.ADMIN)
# def admin_dashboard(request):
#     pass
```

### Multi-Factor Authentication (MFA)

```python
# backend/authentication/mfa.py
import pyotp
import qrcode
import io
import base64
from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string

class MFAHandler:
    @staticmethod
    def generate_secret(user):
        """Generate TOTP secret for user"""
        secret = pyotp.random_base32()
        
        # Store secret temporarily (user must verify before saving)
        cache.set(f'mfa_setup_{user.id}', secret, timeout=300)  # 5 minutes
        
        return secret
    
    @staticmethod
    def generate_qr_code(user, secret):
        """Generate QR code for TOTP setup"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='ClientNest'
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color='black', back_color='white')
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f'data:image/png;base64,{img_str}'
    
    @staticmethod
    def verify_totp(user, token):
        """Verify TOTP token"""
        if not user.mfa_secret:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token, valid_window=1)  # Allow 30s window
    
    @staticmethod
    def generate_backup_codes(user):
        """Generate backup codes for MFA"""
        codes = []
        for _ in range(10):
            code = get_random_string(8, '0123456789')
            codes.append(code)
        
        # Hash and store backup codes
        hashed_codes = [bcrypt.hashpw(code.encode(), bcrypt.gensalt()) for code in codes]
        user.mfa_backup_codes = hashed_codes
        user.save()
        
        return codes
    
    @staticmethod
    def verify_backup_code(user, code):
        """Verify and consume backup code"""
        if not user.mfa_backup_codes:
            return False
        
        for i, hashed_code in enumerate(user.mfa_backup_codes):
            if bcrypt.checkpw(code.encode(), hashed_code):
                # Remove used backup code
                user.mfa_backup_codes.pop(i)
                user.save()
                return True
        
        return False
```

## Data Protection

### Encryption at Rest

```python
# backend/security/encryption.py
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os

class DataEncryption:
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY.encode()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, str):
            data = data.encode()
        
        encrypted_data = self.cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt sensitive data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    @staticmethod
    def generate_key():
        """Generate new encryption key"""
        return Fernet.generate_key().decode()

# Database field encryption
from django.db import models

class EncryptedTextField(models.TextField):
    """Custom field that automatically encrypts/decrypts data"""
    
    def __init__(self, *args, **kwargs):
        self.encryption = DataEncryption()
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.encryption.decrypt(value)
    
    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return self.encryption.decrypt(value)
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.encryption.encrypt(value)

# Usage in models
class SocialMediaAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)
    account_id = models.CharField(max_length=100)
    access_token = EncryptedTextField()  # Encrypted field
    refresh_token = EncryptedTextField()  # Encrypted field
    created_at = models.DateTimeField(auto_now_add=True)
```

### Database Security

```python
# backend/settings/security.py

# Database security settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Force SSL connection
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=serializable'
        },
        'CONN_MAX_AGE': 600,
    }
}

# SQL injection prevention
class SecureQuerySet(models.QuerySet):
    """Custom QuerySet with additional security checks"""
    
    def raw(self, raw_query, params=None, translations=None, using=None):
        # Log raw queries for security monitoring
        logger.warning(f'Raw SQL query executed: {raw_query}')
        return super().raw(raw_query, params, translations, using)
    
    def extra(self, select=None, where=None, params=None, tables=None,
              order_by=None, select_params=None):
        # Log extra queries
        logger.warning(f'Extra SQL query executed: {where}')
        return super().extra(select, where, params, tables, order_by, select_params)

class SecureManager(models.Manager):
    def get_queryset(self):
        return SecureQuerySet(self.model, using=self._db)

# Database audit logging
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    table_name = models.CharField(max_length=100)
    record_id = models.CharField(max_length=100)
    old_values = models.JSONField(null=True)
    new_values = models.JSONField(null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['table_name', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

def log_model_changes(sender, instance, created, **kwargs):
    """Signal handler to log model changes"""
    action = 'CREATE' if created else 'UPDATE'
    
    # Get request context
    request = getattr(instance, '_request', None)
    if request:
        AuditLog.objects.create(
            user=getattr(request, 'user', None),
            action=action,
            table_name=sender._meta.db_table,
            record_id=str(instance.pk),
            new_values=model_to_dict(instance),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
```

## API Security

### Input Validation & Sanitization

```python
# backend/security/validation.py
import re
import bleach
from django.core.exceptions import ValidationError
from rest_framework import serializers

class SecurityValidator:
    @staticmethod
    def validate_email(email):
        """Validate email format and check for suspicious patterns"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError('Invalid email format')
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'[<>"\']',  # HTML/script injection
            r'javascript:',  # JavaScript injection
            r'data:',  # Data URI
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                raise ValidationError('Email contains suspicious content')
        
        return email
    
    @staticmethod
    def sanitize_html(content):
        """Sanitize HTML content to prevent XSS"""
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
        ]
        
        allowed_attributes = {
            '*': ['class'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
        }
        
        return bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def validate_file_upload(file):
        """Validate uploaded files"""
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise ValidationError('File size exceeds 10MB limit')
        
        # Check file type
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/webm', 'video/quicktime'
        ]
        
        if file.content_type not in allowed_types:
            raise ValidationError('File type not allowed')
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.mov']
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise ValidationError('File extension not allowed')
        
        return file
    
    @staticmethod
    def validate_social_content(content):
        """Validate social media content"""
        # Check content length
        if len(content) > 2000:
            raise ValidationError('Content exceeds maximum length')
        
        # Check for malicious patterns
        malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
            r'data:text/html',  # HTML data URIs
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                raise ValidationError('Content contains suspicious elements')
        
        return SecurityValidator.sanitize_html(content)

# Custom serializer fields with validation
class SecureCharField(serializers.CharField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return SecurityValidator.sanitize_html(data)

class SecureEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return SecurityValidator.validate_email(data)

class SecureFileField(serializers.FileField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return SecurityValidator.validate_file_upload(data)
```

### Rate Limiting

```python
# backend/security/rate_limiting.py
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_requests, window_seconds, key_func=None):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_func = key_func or self._default_key_func
    
    def _default_key_func(self, request):
        """Default key function using IP address"""
        return f"rate_limit:{self._get_client_ip(request)}"
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def is_allowed(self, request):
        """Check if request is allowed"""
        key = self.key_func(request)
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Get current requests in window
        requests_key = f"{key}:requests"
        requests = cache.get(requests_key, [])
        
        # Remove old requests
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        if len(requests) >= self.max_requests:
            return False, len(requests)
        
        # Add current request
        requests.append(current_time)
        cache.set(requests_key, requests, self.window_seconds)
        
        return True, len(requests)
    
    def __call__(self, view_func):
        """Decorator to apply rate limiting"""
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            allowed, current_requests = self.is_allowed(request)
            
            if not allowed:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f'Maximum {self.max_requests} requests per {self.window_seconds} seconds',
                    'retry_after': self.window_seconds
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Add rate limit headers
            response = view_func(request, *args, **kwargs)
            response['X-RateLimit-Limit'] = str(self.max_requests)
            response['X-RateLimit-Remaining'] = str(self.max_requests - current_requests)
            response['X-RateLimit-Reset'] = str(int(time.time()) + self.window_seconds)
            
            return response
        return wrapper

# Different rate limits for different endpoints
class RateLimitConfig:
    # Authentication endpoints
    LOGIN_RATE_LIMIT = RateLimiter(5, 300)  # 5 attempts per 5 minutes
    REGISTER_RATE_LIMIT = RateLimiter(3, 3600)  # 3 attempts per hour
    PASSWORD_RESET_RATE_LIMIT = RateLimiter(3, 3600)  # 3 attempts per hour
    
    # API endpoints
    API_RATE_LIMIT = RateLimiter(1000, 3600)  # 1000 requests per hour
    AI_RATE_LIMIT = RateLimiter(100, 3600)  # 100 AI requests per hour
    UPLOAD_RATE_LIMIT = RateLimiter(50, 3600)  # 50 uploads per hour
    
    # User-specific rate limits
    @staticmethod
    def user_rate_limit(max_requests, window_seconds):
        def key_func(request):
            user_id = getattr(request, 'user_id', None)
            if user_id:
                return f"rate_limit:user:{user_id}"
            return f"rate_limit:ip:{RateLimiter._get_client_ip(request)}"
        
        return RateLimiter(max_requests, window_seconds, key_func)

# Usage examples:
# @RateLimitConfig.LOGIN_RATE_LIMIT
# def login_view(request):
#     pass
#
# @RateLimitConfig.user_rate_limit(500, 3600)
# def api_view(request):
#     pass
```

### CORS & Security Headers

```python
# backend/security/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self' https://api.deepseek.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS (only in production with HTTPS)
        if settings.SECURE_SSL_REDIRECT:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Remove server information
        response['Server'] = 'ClientNest'
        
        return response

class CSRFMiddleware(MiddlewareMixin):
    """Custom CSRF protection for API endpoints"""
    
    def process_request(self, request):
        # Skip CSRF for API endpoints using JWT
        if request.path.startswith('/api/') and request.META.get('HTTP_AUTHORIZATION'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return None

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://clientnest.com",
    "https://app.clientnest.com",
    "https://staging.clientnest.com",
]

if settings.DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

## Infrastructure Security

### AWS Security Configuration

```yaml
# infrastructure/security/security-groups.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Security Groups for ClientNest'

Resources:
  # Web Application Security Group
  WebAppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web application
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS traffic
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP traffic (redirect to HTTPS)
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: Outbound HTTPS
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          DestinationSecurityGroupId: !Ref DatabaseSecurityGroup
          Description: Database access
      Tags:
        - Key: Name
          Value: ClientNest-WebApp-SG

  # Database Security Group
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for database
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref WebAppSecurityGroup
          Description: Database access from web app
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref BastionSecurityGroup
          Description: Database access from bastion
      Tags:
        - Key: Name
          Value: ClientNest-Database-SG

  # Bastion Host Security Group
  BastionSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for bastion host
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AdminCIDR
          Description: SSH access from admin IPs
      Tags:
        - Key: Name
          Value: ClientNest-Bastion-SG

  # Redis Security Group
  RedisSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Redis
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref WebAppSecurityGroup
          Description: Redis access from web app
      Tags:
        - Key: Name
          Value: ClientNest-Redis-SG
```

### IAM Policies

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3MediaAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::clientnest-media/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "S3MediaBucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::clientnest-media"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/clientnest-*"
    },
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:clientnest/*"
    }
  ]
}
```

## Monitoring & Incident Response

### Security Monitoring

```python
# backend/security/monitoring.py
import logging
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.core.cache import cache

class SecurityMonitor:
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_security_event(self, event_type, details, severity='medium', user=None, ip_address=None):
        """Log security events"""
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'user_id': user.id if user else None,
            'ip_address': ip_address,
        }
        
        self.logger.warning(f'Security Event: {event_type}', extra=event_data)
        
        # Alert on high severity events
        if severity == 'high':
            self._send_security_alert(event_data)
    
    def detect_brute_force(self, ip_address, user_id=None):
        """Detect brute force attacks"""
        key = f'failed_attempts:{ip_address}'
        if user_id:
            key += f':{user_id}'
        
        attempts = cache.get(key, 0)
        attempts += 1
        cache.set(key, attempts, 3600)  # 1 hour
        
        if attempts >= 5:
            self.log_security_event(
                'BRUTE_FORCE_DETECTED',
                f'Multiple failed login attempts from {ip_address}',
                severity='high',
                ip_address=ip_address
            )
            return True
        
        return False
    
    def detect_anomalous_activity(self, user, request):
        """Detect anomalous user activity"""
        # Check for unusual login location
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = self._get_client_ip(request)
        
        # Store user's typical patterns
        pattern_key = f'user_patterns:{user.id}'
        patterns = cache.get(pattern_key, {
            'ips': [],
            'user_agents': [],
            'login_times': []
        })
        
        # Check for new IP
        if ip_address not in patterns['ips']:
            self.log_security_event(
                'NEW_IP_LOGIN',
                f'User {user.email} logged in from new IP: {ip_address}',
                severity='medium',
                user=user,
                ip_address=ip_address
            )
        
        # Check for new user agent
        if user_agent not in patterns['user_agents']:
            self.log_security_event(
                'NEW_DEVICE_LOGIN',
                f'User {user.email} logged in from new device',
                severity='medium',
                user=user,
                ip_address=ip_address
            )
        
        # Update patterns
        patterns['ips'] = list(set(patterns['ips'] + [ip_address]))[-10:]  # Keep last 10
        patterns['user_agents'] = list(set(patterns['user_agents'] + [user_agent]))[-5:]  # Keep last 5
        patterns['login_times'].append(datetime.utcnow().isoformat())
        patterns['login_times'] = patterns['login_times'][-20:]  # Keep last 20
        
        cache.set(pattern_key, patterns, 86400 * 30)  # 30 days
    
    def _send_security_alert(self, event_data):
        """Send security alert to administrators"""
        subject = f'Security Alert: {event_data["event_type"]}'
        message = f"""
        Security Event Detected:
        
        Type: {event_data['event_type']}
        Severity: {event_data['severity']}
        Time: {event_data['timestamp']}
        Details: {event_data['details']}
        User ID: {event_data.get('user_id', 'N/A')}
        IP Address: {event_data.get('ip_address', 'N/A')}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            settings.SECURITY_ALERT_EMAILS,
            fail_silently=False,
        )
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

# Security monitoring middleware
class SecurityMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.monitor = SecurityMonitor()
    
    def __call__(self, request):
        # Monitor suspicious requests
        self._check_suspicious_requests(request)
        
        response = self.get_response(request)
        
        # Monitor response patterns
        self._check_response_patterns(request, response)
        
        return response
    
    def _check_suspicious_requests(self, request):
        # Check for SQL injection attempts
        query_params = str(request.GET) + str(request.POST)
        sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'insert\s+into',
            r'delete\s+from',
            r'update\s+.*set',
            r'exec\s*\(',
            r'script\s*>',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, query_params, re.IGNORECASE):
                self.monitor.log_security_event(
                    'SQL_INJECTION_ATTEMPT',
                    f'Suspicious query detected: {pattern}',
                    severity='high',
                    ip_address=self.monitor._get_client_ip(request)
                )
                break
    
    def _check_response_patterns(self, request, response):
        # Monitor for information disclosure
        if response.status_code == 500 and settings.DEBUG:
            self.monitor.log_security_event(
                'DEBUG_INFO_DISCLOSURE',
                'Debug information exposed in production',
                severity='medium',
                ip_address=self.monitor._get_client_ip(request)
            )
```

## Compliance & Privacy

### GDPR Compliance

```python
# backend/privacy/gdpr.py
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class DataProcessingPurpose(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    legal_basis = models.CharField(max_length=50, choices=[
        ('consent', 'Consent'),
        ('contract', 'Contract'),
        ('legal_obligation', 'Legal Obligation'),
        ('vital_interests', 'Vital Interests'),
        ('public_task', 'Public Task'),
        ('legitimate_interests', 'Legitimate Interests'),
    ])
    retention_period = models.IntegerField(help_text='Retention period in days')
    created_at = models.DateTimeField(auto_now_add=True)

class UserConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purpose = models.ForeignKey(DataProcessingPurpose, on_delete=models.CASCADE)
    consented = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    withdrawal_date = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    class Meta:
        unique_together = ['user', 'purpose']

class DataExportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    export_file = models.FileField(upload_to='exports/', null=True, blank=True)
    
class DataDeletionRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)

class GDPRManager:
    @staticmethod
    def export_user_data(user):
        """Export all user data for GDPR compliance"""
        data = {
            'user_profile': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'social_accounts': [],
            'posts': [],
            'comments': [],
            'analytics': [],
            'billing': [],
        }
        
        # Export social media accounts (encrypted data)
        for account in user.socialmediaaccount_set.all():
            data['social_accounts'].append({
                'platform': account.platform,
                'account_id': account.account_id,
                'connected_at': account.created_at.isoformat(),
            })
        
        # Export posts
        for post in user.post_set.all():
            data['posts'].append({
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'platforms': post.platforms,
                'status': post.status,
                'created_at': post.created_at.isoformat(),
                'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
            })
        
        # Export other user data...
        
        return data
    
    @staticmethod
    def delete_user_data(user, keep_legal_records=True):
        """Delete user data for GDPR compliance"""
        # Anonymize instead of delete for legal/audit purposes
        if keep_legal_records:
            user.email = f'deleted_user_{user.id}@example.com'
            user.first_name = 'Deleted'
            user.last_name = 'User'
            user.is_active = False
            user.save()
        else:
            # Complete deletion
            user.delete()
        
        # Delete associated data
        user.socialmediaaccount_set.all().delete()
        user.post_set.all().delete()
        user.comment_set.all().delete()
        
        # Keep audit logs for legal compliance
        # user.auditlog_set.all().delete()  # Don't delete audit logs
    
    @staticmethod
    def check_data_retention():
        """Check and enforce data retention policies"""
        for purpose in DataProcessingPurpose.objects.all():
            cutoff_date = datetime.now() - timedelta(days=purpose.retention_period)
            
            # Find data that should be deleted
            if purpose.name == 'analytics':
                # Delete old analytics data
                from analytics.models import AnalyticsEvent
                AnalyticsEvent.objects.filter(
                    created_at__lt=cutoff_date
                ).delete()
            
            elif purpose.name == 'audit_logs':
                # Delete old audit logs
                AuditLog.objects.filter(
                    timestamp__lt=cutoff_date
                ).delete()
```

---

*This security architecture provides comprehensive protection for ClientNest across all layers, from frontend to database, with monitoring, compliance, and incident response capabilities.*