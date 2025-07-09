from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.cache import cache
from django.utils import timezone
from .models import User, UserActivity, UserSession
from .utils import (
    log_user_activity, get_client_ip, send_welcome_email,
    register_service_with_gateway
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Handle actions after user is saved.
    """
    if created:
        # Log user creation
        logger.info(f"New user created: {instance.email}")
        
        # Send welcome email for verified users
        if instance.is_verified:
            try:
                send_welcome_email(instance)
            except Exception as e:
                logger.error(f"Failed to send welcome email to {instance.email}: {str(e)}")
        
        # Create initial activity log
        try:
            UserActivity.objects.create(
                user=instance,
                activity_type='account_created',
                ip_address='127.0.0.1',  # Default for system-created users
                details={
                    'registration_method': 'email',
                    'is_verified': instance.is_verified
                }
            )
        except Exception as e:
            logger.error(f"Failed to create initial activity log for {instance.email}: {str(e)}")
    
    else:
        # Handle user updates
        if hasattr(instance, '_state') and instance._state.adding is False:
            # Check if verification status changed
            try:
                old_instance = User.objects.get(pk=instance.pk)
                if not old_instance.is_verified and instance.is_verified:
                    # User just got verified
                    logger.info(f"User verified: {instance.email}")
                    
                    # Send welcome email
                    try:
                        send_welcome_email(instance)
                    except Exception as e:
                        logger.error(f"Failed to send welcome email to {instance.email}: {str(e)}")
                
                # Check if premium status changed
                if not old_instance.is_premium and instance.is_premium:
                    logger.info(f"User became premium: {instance.email}")
                    
                    # Log premium upgrade
                    UserActivity.objects.create(
                        user=instance,
                        activity_type='premium_upgrade',
                        ip_address='127.0.0.1',
                        details={'upgraded_at': timezone.now().isoformat()}
                    )
                    
            except User.DoesNotExist:
                pass
            except Exception as e:
                logger.error(f"Error in user post_save signal: {str(e)}")
    
    # Clear user cache
    cache_key = f"user_{instance.pk}"
    cache.delete(cache_key)


@receiver(pre_delete, sender=User)
def user_pre_delete(sender, instance, **kwargs):
    """
    Handle actions before user is deleted.
    """
    logger.info(f"User being deleted: {instance.email}")
    
    # Log user deletion
    try:
        UserActivity.objects.create(
            user=instance,
            activity_type='account_deleted',
            ip_address='127.0.0.1',
            details={
                'deleted_at': timezone.now().isoformat(),
                'was_verified': instance.is_verified,
                'was_premium': instance.is_premium
            }
        )
    except Exception as e:
        logger.error(f"Failed to log user deletion for {instance.email}: {str(e)}")
    
    # Deactivate all user sessions
    try:
        UserSession.objects.filter(user=instance).update(is_active=False)
    except Exception as e:
        logger.error(f"Failed to deactivate sessions for {instance.email}: {str(e)}")


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    """
    Handle actions after user is deleted.
    """
    logger.info(f"User deleted: {instance.email}")
    
    # Clear user cache
    cache_key = f"user_{instance.pk}"
    cache.delete(cache_key)
    
    # Clear any related caches
    cache.delete(f"user_profile_{instance.pk}")
    cache.delete(f"user_sessions_{instance.pk}")
    cache.delete(f"user_activities_{instance.pk}")


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Handle user login signal.
    """
    try:
        # Update last login IP
        if request:
            ip_address = get_client_ip(request)
            user.update_last_login_ip(ip_address)
            
            # Create or update session record
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.update_or_create(
                    user=user,
                    session_key=session_key,
                    defaults={
                        'ip_address': ip_address,
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'last_activity': timezone.now(),
                        'is_active': True
                    }
                )
            
            # Log login activity
            log_user_activity(
                user=user,
                activity_type='login',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'login_method': 'session'}
            )
        
        logger.info(f"User logged in: {user.email}")
        
    except Exception as e:
        logger.error(f"Error in user_logged_in signal: {str(e)}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    Handle user logout signal.
    """
    try:
        if user and request:
            # Deactivate session
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(
                    user=user,
                    session_key=session_key
                ).update(is_active=False)
            
            # Log logout activity
            log_user_activity(
                user=user,
                activity_type='logout',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'logout_method': 'session'}
            )
            
            logger.info(f"User logged out: {user.email}")
        
    except Exception as e:
        logger.error(f"Error in user_logged_out signal: {str(e)}")


@receiver(post_save, sender=UserActivity)
def user_activity_post_save(sender, instance, created, **kwargs):
    """
    Handle actions after user activity is logged.
    """
    if created:
        # Update user's last activity timestamp
        try:
            User.objects.filter(pk=instance.user.pk).update(
                updated_at=timezone.now()
            )
        except Exception as e:
            logger.error(f"Failed to update user last activity: {str(e)}")
        
        # Check for suspicious activity patterns
        try:
            recent_activities = UserActivity.objects.filter(
                user=instance.user,
                timestamp__gte=timezone.now() - timezone.timedelta(minutes=5)
            ).count()
            
            # If more than 10 activities in 5 minutes, log as suspicious
            if recent_activities > 10:
                logger.warning(
                    f"Suspicious activity detected for user {instance.user.email}: "
                    f"{recent_activities} activities in 5 minutes"
                )
                
                # Create a suspicious activity log
                UserActivity.objects.create(
                    user=instance.user,
                    activity_type='suspicious_activity_detected',
                    ip_address=instance.ip_address,
                    details={
                        'recent_activity_count': recent_activities,
                        'detection_time': timezone.now().isoformat()
                    }
                )
        
        except Exception as e:
            logger.error(f"Error checking suspicious activity: {str(e)}")


@receiver(post_save, sender=UserSession)
def user_session_post_save(sender, instance, created, **kwargs):
    """
    Handle actions after user session is saved.
    """
    if created:
        logger.info(f"New session created for user: {instance.user.email}")
        
        # Check for multiple active sessions
        try:
            active_sessions = UserSession.objects.filter(
                user=instance.user,
                is_active=True
            ).count()
            
            # If more than 5 active sessions, log as suspicious
            if active_sessions > 5:
                logger.warning(
                    f"Multiple active sessions detected for user {instance.user.email}: "
                    f"{active_sessions} sessions"
                )
                
                # Log suspicious session activity
                log_user_activity(
                    user=instance.user,
                    activity_type='multiple_sessions_detected',
                    ip_address=instance.ip_address,
                    details={
                        'active_session_count': active_sessions,
                        'detection_time': timezone.now().isoformat()
                    }
                )
        
        except Exception as e:
            logger.error(f"Error checking multiple sessions: {str(e)}")


# Application startup signal
def register_service_on_startup():
    """
    Register service with API Gateway on startup.
    """
    try:
        register_service_with_gateway()
    except Exception as e:
        logger.error(f"Failed to register service on startup: {str(e)}")


# Cache warming signals
@receiver(post_save, sender=User)
def warm_user_cache(sender, instance, **kwargs):
    """
    Warm up cache for frequently accessed user data.
    """
    try:
        # Cache user profile data
        cache_key = f"user_profile_{instance.pk}"
        cache.set(cache_key, {
            'id': instance.pk,
            'email': instance.email,
            'username': instance.username,
            'full_name': instance.get_full_name(),
            'is_verified': instance.is_verified,
            'is_premium': instance.is_premium,
            'profile_picture': instance.profile_picture.url if instance.profile_picture else None
        }, timeout=3600)  # Cache for 1 hour
        
    except Exception as e:
        logger.error(f"Error warming user cache: {str(e)}")