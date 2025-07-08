from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserActivity
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


def log_user_activity(
    user,
    activity_type: str,
    ip_address: str,
    user_agent: str = '',
    details: Optional[Dict[str, Any]] = None
) -> UserActivity:
    """
    Log user activity.
    """
    try:
        activity = UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        logger.info(f"User activity logged: {user.email} - {activity_type}")
        return activity
    except Exception as e:
        logger.error(f"Failed to log user activity: {str(e)}")
        return None


def send_verification_email(user, request) -> bool:
    """
    Send email verification to user.
    """
    try:
        # Generate verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
        
        # Email context
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': getattr(settings, 'SITE_NAME', 'ClientNest'),
            'domain': getattr(settings, 'DOMAIN', 'localhost')
        }
        
        # Render email templates
        subject = render_to_string('emails/verification_subject.txt', context).strip()
        html_message = render_to_string('emails/verification_email.html', context)
        text_message = render_to_string('emails/verification_email.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user, request) -> bool:
    """
    Send password reset email to user.
    """
    try:
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Email context
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': getattr(settings, 'SITE_NAME', 'ClientNest'),
            'domain': getattr(settings, 'DOMAIN', 'localhost')
        }
        
        # Render email templates
        subject = render_to_string('emails/password_reset_subject.txt', context).strip()
        html_message = render_to_string('emails/password_reset_email.html', context)
        text_message = render_to_string('emails/password_reset_email.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user) -> bool:
    """
    Send welcome email to new user.
    """
    try:
        # Email context
        context = {
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'ClientNest'),
            'domain': getattr(settings, 'DOMAIN', 'localhost'),
            'login_url': f"{settings.FRONTEND_URL}/login/"
        }
        
        # Render email templates
        subject = render_to_string('emails/welcome_subject.txt', context).strip()
        html_message = render_to_string('emails/welcome_email.html', context)
        text_message = render_to_string('emails/welcome_email.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate phone number format.
    """
    try:
        from phonenumber_field.phonenumber import PhoneNumber
        phone = PhoneNumber.from_string(phone_number)
        return phone.is_valid()
    except Exception:
        return False


def generate_username_from_email(email: str) -> str:
    """
    Generate a unique username from email.
    """
    from .models import User
    
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username


def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Check password strength and return feedback.
    """
    import re
    
    feedback = {
        'score': 0,
        'is_strong': False,
        'suggestions': []
    }
    
    # Length check
    if len(password) >= 8:
        feedback['score'] += 1
    else:
        feedback['suggestions'].append('Use at least 8 characters')
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        feedback['score'] += 1
    else:
        feedback['suggestions'].append('Include uppercase letters')
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        feedback['score'] += 1
    else:
        feedback['suggestions'].append('Include lowercase letters')
    
    # Number check
    if re.search(r'\d', password):
        feedback['score'] += 1
    else:
        feedback['suggestions'].append('Include numbers')
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        feedback['score'] += 1
    else:
        feedback['suggestions'].append('Include special characters')
    
    # Common password check
    common_passwords = [
        'password', '123456', 'password123', 'admin', 'qwerty',
        'letmein', 'welcome', 'monkey', '1234567890'
    ]
    if password.lower() in common_passwords:
        feedback['score'] -= 2
        feedback['suggestions'].append('Avoid common passwords')
    
    feedback['is_strong'] = feedback['score'] >= 4
    return feedback


def register_service_with_gateway() -> bool:
    """
    Register this service with the API Gateway.
    """
    try:
        gateway_url = getattr(settings, 'API_GATEWAY_URL', None)
        if not gateway_url:
            logger.warning("API Gateway URL not configured")
            return False
        
        service_data = {
            'name': settings.SERVICE_NAME,
            'version': settings.SERVICE_VERSION,
            'host': getattr(settings, 'SERVICE_HOST', 'localhost'),
            'port': getattr(settings, 'SERVICE_PORT', 8001),
            'health_check_url': '/api/health/',
            'description': 'User management microservice',
            'tags': ['user', 'authentication', 'profile']
        }
        
        response = requests.post(
            f"{gateway_url}/api/services/register/",
            json=service_data,
            timeout=10
        )
        
        if response.status_code == 201:
            logger.info("Service registered with API Gateway successfully")
            return True
        else:
            logger.error(f"Failed to register with API Gateway: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error registering with API Gateway: {str(e)}")
        return False


def cleanup_expired_sessions() -> int:
    """
    Clean up expired user sessions.
    """
    from .models import UserSession
    from datetime import timedelta
    
    try:
        # Sessions inactive for more than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        expired_sessions = UserSession.objects.filter(
            last_activity__lt=cutoff_date
        )
        
        count = expired_sessions.count()
        expired_sessions.delete()
        
        logger.info(f"Cleaned up {count} expired sessions")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {str(e)}")
        return 0


def get_user_location_from_ip(ip_address: str) -> Optional[Dict[str, str]]:
    """
    Get user location from IP address using a geolocation service.
    """
    try:
        # Using a free IP geolocation service
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'timezone': data.get('timezone')
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting location for IP {ip_address}: {str(e)}")
        return None


def sanitize_user_input(input_string: str) -> str:
    """
    Sanitize user input to prevent XSS and other attacks.
    """
    import html
    import re
    
    # HTML escape
    sanitized = html.escape(input_string)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick='
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()