from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

from .models import UserProfile, UserPreference, UserSkill, UserEducation, UserExperience
from .utils import (
    calculate_profile_completion,
    clear_user_profile_cache,
    cache_user_profile,
    send_profile_completion_reminder,
    log_profile_activity
)

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile_and_preferences(sender, instance, created, **kwargs):
    """
    Create UserProfile and UserPreference when a new user is created.
    """
    if created:
        try:
            # Create user profile
            UserProfile.objects.create(user=instance)
            logger.info(f"Created profile for user {instance.id}")
            
            # Create user preferences with defaults
            UserPreference.objects.create(
                user=instance,
                theme='light',
                language='en',
                timezone='UTC',
                email_notifications=True,
                push_notifications=True,
                profile_visibility='public'
            )
            logger.info(f"Created preferences for user {instance.id}")
            
            # Log activity
            log_profile_activity(
                user=instance,
                activity_type='profile_created',
                details={'auto_created': True}
            )
            
        except Exception as e:
            logger.error(f"Failed to create profile/preferences for user {instance.id}: {e}")


@receiver(post_save, sender=UserProfile)
def handle_profile_update(sender, instance, created, **kwargs):
    """
    Handle profile updates and cache management.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Calculate completion percentage
        completion_data = calculate_profile_completion(instance)
        
        # Cache updated profile data
        profile_data = {
            'id': instance.id,
            'completion_percentage': completion_data['overall_percentage'],
            'is_complete': completion_data['is_complete'],
            'last_updated': timezone.now().isoformat()
        }
        cache_user_profile(instance.user.id, profile_data)
        
        # Log activity
        activity_type = 'profile_created' if created else 'profile_updated'
        log_profile_activity(
            user=instance.user,
            activity_type=activity_type,
            details={
                'completion_percentage': completion_data['overall_percentage'],
                'fields_updated': kwargs.get('update_fields', [])
            }
        )
        
        # Send completion reminder if profile is incomplete
        if not created and completion_data['overall_percentage'] < 80:
            # Check if we haven't sent a reminder recently
            cache_key = f"completion_reminder_{instance.user.id}"
            if not cache.get(cache_key):
                send_profile_completion_reminder(
                    user_email=instance.user.email,
                    user_name=instance.user.get_full_name() or instance.user.email,
                    completion_percentage=completion_data['overall_percentage']
                )
                # Set cache to prevent spam (24 hours)
                cache.set(cache_key, True, timeout=86400)
        
        logger.info(f"Profile {'created' if created else 'updated'} for user {instance.user.id}")
        
    except Exception as e:
        logger.error(f"Error handling profile update for user {instance.user.id}: {e}")


@receiver(post_save, sender=UserPreference)
def handle_preference_update(sender, instance, created, **kwargs):
    """
    Handle preference updates.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Log activity
        activity_type = 'preferences_created' if created else 'preferences_updated'
        log_profile_activity(
            user=instance.user,
            activity_type=activity_type,
            details={
                'theme': instance.theme,
                'language': instance.language,
                'timezone': instance.timezone
            }
        )
        
        logger.info(f"Preferences {'created' if created else 'updated'} for user {instance.user.id}")
        
    except Exception as e:
        logger.error(f"Error handling preference update for user {instance.user.id}: {e}")


@receiver(post_save, sender=UserSkill)
def handle_skill_update(sender, instance, created, **kwargs):
    """
    Handle skill additions and updates.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Log activity
        activity_type = 'skill_added' if created else 'skill_updated'
        log_profile_activity(
            user=instance.user,
            activity_type=activity_type,
            details={
                'skill_name': instance.skill_name,
                'proficiency_level': instance.proficiency_level,
                'years_of_experience': instance.years_of_experience
            }
        )
        
        # Check for skill milestones
        if created:
            skill_count = UserSkill.objects.filter(user=instance.user).count()
            milestones = [5, 10, 20, 50]
            
            if skill_count in milestones:
                log_profile_activity(
                    user=instance.user,
                    activity_type='skill_milestone',
                    details={
                        'milestone': skill_count,
                        'message': f'Added {skill_count} skills to profile'
                    }
                )
        
        logger.info(f"Skill {'added' if created else 'updated'} for user {instance.user.id}: {instance.skill_name}")
        
    except Exception as e:
        logger.error(f"Error handling skill update for user {instance.user.id}: {e}")


@receiver(post_save, sender=UserEducation)
def handle_education_update(sender, instance, created, **kwargs):
    """
    Handle education record additions and updates.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Log activity
        activity_type = 'education_added' if created else 'education_updated'
        log_profile_activity(
            user=instance.user,
            activity_type=activity_type,
            details={
                'institution_name': instance.institution_name,
                'degree_type': instance.degree_type,
                'field_of_study': instance.field_of_study
            }
        )
        
        logger.info(f"Education {'added' if created else 'updated'} for user {instance.user.id}: {instance.institution_name}")
        
    except Exception as e:
        logger.error(f"Error handling education update for user {instance.user.id}: {e}")


@receiver(post_save, sender=UserExperience)
def handle_experience_update(sender, instance, created, **kwargs):
    """
    Handle work experience additions and updates.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Log activity
        activity_type = 'experience_added' if created else 'experience_updated'
        log_profile_activity(
            user=instance.user,
            activity_type=activity_type,
            details={
                'company_name': instance.company_name,
                'job_title': instance.job_title,
                'employment_type': instance.employment_type,
                'is_current': instance.is_current
            }
        )
        
        # Check for career milestones
        if created:
            experience_count = UserExperience.objects.filter(user=instance.user).count()
            total_years = sum(
                exp.duration_years for exp in UserExperience.objects.filter(user=instance.user)
                if exp.duration_years
            )
            
            if experience_count == 1:
                log_profile_activity(
                    user=instance.user,
                    activity_type='career_milestone',
                    details={
                        'milestone': 'first_job',
                        'message': 'Added first work experience'
                    }
                )
            elif total_years >= 5:
                log_profile_activity(
                    user=instance.user,
                    activity_type='career_milestone',
                    details={
                        'milestone': 'experienced_professional',
                        'total_years': total_years,
                        'message': f'Reached {total_years} years of experience'
                    }
                )
        
        logger.info(f"Experience {'added' if created else 'updated'} for user {instance.user.id}: {instance.company_name}")
        
    except Exception as e:
        logger.error(f"Error handling experience update for user {instance.user.id}: {e}")


@receiver(post_delete, sender=UserSkill)
def handle_skill_deletion(sender, instance, **kwargs):
    """
    Handle skill deletions.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Log activity
        log_profile_activity(
            user=instance.user,
            activity_type='skill_removed',
            details={
                'skill_name': instance.skill_name,
                'proficiency_level': instance.proficiency_level
            }
        )
        
        logger.info(f"Skill removed for user {instance.user.id}: {instance.skill_name}")
        
    except Exception as e:
        logger.error(f"Error handling skill deletion for user {instance.user.id}: {e}")


@receiver(post_delete, sender=UserEducation)
def handle_education_deletion(sender, instance, **kwargs):
    """
    Handle education record deletions.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Log activity
        log_profile_activity(
            user=instance.user,
            activity_type='education_removed',
            details={
                'institution_name': instance.institution_name,
                'degree_type': instance.degree_type
            }
        )
        
        logger.info(f"Education removed for user {instance.user.id}: {instance.institution_name}")
        
    except Exception as e:
        logger.error(f"Error handling education deletion for user {instance.user.id}: {e}")


@receiver(post_delete, sender=UserExperience)
def handle_experience_deletion(sender, instance, **kwargs):
    """
    Handle work experience deletions.
    """
    try:
        # Clear cache
        clear_user_profile_cache(instance.user.id)
        
        # Log activity
        log_profile_activity(
            user=instance.user,
            activity_type='experience_removed',
            details={
                'company_name': instance.company_name,
                'job_title': instance.job_title
            }
        )
        
        logger.info(f"Experience removed for user {instance.user.id}: {instance.company_name}")
        
    except Exception as e:
        logger.error(f"Error handling experience deletion for user {instance.user.id}: {e}")


@receiver(pre_save, sender=UserProfile)
def validate_profile_before_save(sender, instance, **kwargs):
    """
    Validate profile data before saving.
    """
    try:
        # Validate social URLs
        from .utils import validate_social_url
        
        social_fields = {
            'linkedin_url': 'linkedin',
            'twitter_url': 'twitter',
            'facebook_url': 'facebook',
            'instagram_url': 'instagram',
            'github_url': 'github',
            'website': 'website'
        }
        
        for field, platform in social_fields.items():
            url = getattr(instance, field, None)
            if url and not validate_social_url(url, platform):
                logger.warning(f"Invalid {platform} URL for user {instance.user.id}: {url}")
                setattr(instance, field, None)  # Clear invalid URL
        
        # Sanitize bio
        from .utils import sanitize_bio
        if instance.bio:
            instance.bio = sanitize_bio(instance.bio)
        
        # Validate phone number
        from .utils import validate_phone_number
        if instance.phone_number and not validate_phone_number(instance.phone_number):
            logger.warning(f"Invalid phone number for user {instance.user.id}: {instance.phone_number}")
            instance.phone_number = None  # Clear invalid phone
        
    except Exception as e:
        logger.error(f"Error validating profile for user {instance.user.id}: {e}")


@receiver(pre_save, sender=UserSkill)
def validate_skill_before_save(sender, instance, **kwargs):
    """
    Validate skill data before saving.
    """
    try:
        from .utils import validate_skill_name
        
        # Validate skill name
        if not validate_skill_name(instance.skill_name):
            raise ValueError(f"Invalid skill name: {instance.skill_name}")
        
        # Normalize skill name
        instance.skill_name = instance.skill_name.strip().title()
        
        # Validate years of experience
        if instance.years_of_experience < 0:
            instance.years_of_experience = 0
        elif instance.years_of_experience > 50:
            instance.years_of_experience = 50
        
    except Exception as e:
        logger.error(f"Error validating skill for user {instance.user.id}: {e}")
        raise


# Periodic cleanup tasks (these would typically be run via Celery)
def cleanup_incomplete_profiles():
    """
    Clean up profiles that haven't been updated in a long time.
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=365)  # 1 year
        
        incomplete_profiles = UserProfile.objects.filter(
            updated_at__lt=cutoff_date,
            bio__isnull=True
        )
        
        for profile in incomplete_profiles:
            # Send reminder email
            completion_data = calculate_profile_completion(profile)
            if completion_data['overall_percentage'] < 30:
                send_profile_completion_reminder(
                    user_email=profile.user.email,
                    user_name=profile.user.get_full_name() or profile.user.email,
                    completion_percentage=completion_data['overall_percentage']
                )
        
        logger.info(f"Processed {incomplete_profiles.count()} incomplete profiles")
        
    except Exception as e:
        logger.error(f"Error in cleanup_incomplete_profiles: {e}")


def warm_profile_cache():
    """
    Warm up cache for active users' profiles.
    """
    try:
        # Get recently active users
        recent_cutoff = timezone.now() - timedelta(days=7)
        active_users = User.objects.filter(
            last_login__gte=recent_cutoff
        ).select_related('userprofile')
        
        for user in active_users:
            try:
                profile = user.userprofile
                completion_data = calculate_profile_completion(profile)
                
                profile_data = {
                    'id': profile.id,
                    'completion_percentage': completion_data['overall_percentage'],
                    'is_complete': completion_data['is_complete'],
                    'last_updated': profile.updated_at.isoformat()
                }
                
                cache_user_profile(user.id, profile_data)
                
            except UserProfile.DoesNotExist:
                continue
        
        logger.info(f"Warmed cache for {active_users.count()} user profiles")
        
    except Exception as e:
        logger.error(f"Error in warm_profile_cache: {e}")