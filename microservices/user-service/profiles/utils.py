import re
import requests
from typing import Dict, List, Optional, Any
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import json
from PIL import Image
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


def validate_social_url(url: str, platform: str) -> bool:
    """
    Validate social media URLs based on platform.
    """
    if not url:
        return True
    
    patterns = {
        'linkedin': r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$',
        'twitter': r'^https?://(www\.)?(twitter\.com|x\.com)/[\w\-]+/?$',
        'facebook': r'^https?://(www\.)?facebook\.com/[\w\-\.]+/?$',
        'instagram': r'^https?://(www\.)?instagram\.com/[\w\-\.]+/?$',
        'github': r'^https?://(www\.)?github\.com/[\w\-]+/?$',
        'website': r'^https?://[\w\-\.]+(\.[a-zA-Z]{2,})+(/.*)?$'
    }
    
    pattern = patterns.get(platform.lower())
    if pattern:
        return bool(re.match(pattern, url))
    
    return True


def calculate_profile_completion(user_profile) -> Dict[str, Any]:
    """
    Calculate profile completion percentage and missing fields.
    """
    required_fields = [
        'first_name', 'last_name', 'bio', 'date_of_birth',
        'phone_number', 'city', 'country'
    ]
    
    optional_fields = [
        'gender', 'occupation', 'company', 'website',
        'linkedin_url', 'twitter_url'
    ]
    
    completed_required = 0
    completed_optional = 0
    missing_fields = []
    
    # Check required fields
    for field in required_fields:
        if hasattr(user_profile, field):
            value = getattr(user_profile, field)
            if value:
                completed_required += 1
            else:
                missing_fields.append(field)
        elif hasattr(user_profile.user, field):
            value = getattr(user_profile.user, field)
            if value:
                completed_required += 1
            else:
                missing_fields.append(field)
        else:
            missing_fields.append(field)
    
    # Check optional fields
    for field in optional_fields:
        if hasattr(user_profile, field):
            value = getattr(user_profile, field)
            if value:
                completed_optional += 1
    
    required_percentage = (completed_required / len(required_fields)) * 100
    total_fields = len(required_fields) + len(optional_fields)
    total_completed = completed_required + completed_optional
    overall_percentage = (total_completed / total_fields) * 100
    
    return {
        'overall_percentage': round(overall_percentage, 2),
        'required_percentage': round(required_percentage, 2),
        'completed_required': completed_required,
        'total_required': len(required_fields),
        'completed_optional': completed_optional,
        'total_optional': len(optional_fields),
        'missing_fields': missing_fields,
        'is_complete': required_percentage == 100
    }


def validate_phone_number(phone: str, country_code: str = None) -> bool:
    """
    Validate phone number format.
    """
    if not phone:
        return True
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Basic validation patterns
    patterns = {
        'international': r'^\+[1-9]\d{1,14}$',
        'us': r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',
        'uk': r'^\+?44[1-9]\d{8,9}$',
        'general': r'^\+?[1-9]\d{7,14}$'
    }
    
    if country_code and country_code.lower() in patterns:
        pattern = patterns[country_code.lower()]
    else:
        pattern = patterns['general']
    
    return bool(re.match(pattern, cleaned))


def generate_username_suggestions(first_name: str, last_name: str, email: str) -> List[str]:
    """
    Generate username suggestions based on user info.
    """
    suggestions = []
    
    if first_name and last_name:
        base_names = [
            f"{first_name.lower()}{last_name.lower()}",
            f"{first_name.lower()}.{last_name.lower()}",
            f"{first_name.lower()}_{last_name.lower()}",
            f"{first_name[0].lower()}{last_name.lower()}",
            f"{first_name.lower()}{last_name[0].lower()}"
        ]
        suggestions.extend(base_names)
    
    if email:
        email_base = email.split('@')[0]
        suggestions.append(email_base)
    
    # Add numbered variations
    numbered_suggestions = []
    for suggestion in suggestions[:3]:  # Limit to first 3
        for i in range(1, 100):
            numbered_suggestions.append(f"{suggestion}{i}")
            if len(numbered_suggestions) >= 10:
                break
        if len(numbered_suggestions) >= 10:
            break
    
    suggestions.extend(numbered_suggestions)
    
    return list(set(suggestions))[:20]  # Return unique suggestions, max 20


def validate_date_range(start_date: datetime, end_date: datetime = None) -> bool:
    """
    Validate date ranges for education and experience.
    """
    if not start_date:
        return False
    
    # Start date should not be in the future
    if start_date.date() > timezone.now().date():
        return False
    
    # If end date is provided, it should be after start date
    if end_date:
        if end_date.date() < start_date.date():
            return False
        # End date should not be more than 1 year in the future
        if end_date.date() > (timezone.now() + timedelta(days=365)).date():
            return False
    
    return True


def sanitize_bio(bio: str) -> str:
    """
    Sanitize bio content to prevent XSS and clean up formatting.
    """
    if not bio:
        return ''
    
    # Remove HTML tags
    bio = strip_tags(bio)
    
    # Remove excessive whitespace
    bio = re.sub(r'\s+', ' ', bio).strip()
    
    # Limit length
    if len(bio) > 1000:
        bio = bio[:997] + '...'
    
    return bio


def validate_skill_name(skill_name: str) -> bool:
    """
    Validate skill name format.
    """
    if not skill_name or len(skill_name.strip()) < 2:
        return False
    
    # Allow letters, numbers, spaces, hyphens, and common symbols
    pattern = r'^[a-zA-Z0-9\s\-\.\+\#\(\)]+$'
    return bool(re.match(pattern, skill_name.strip()))


def get_location_from_ip(ip_address: str) -> Dict[str, str]:
    """
    Get location information from IP address.
    """
    try:
        # Use a free IP geolocation service
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', ''),
                    'region': data.get('regionName', ''),
                    'city': data.get('city', ''),
                    'timezone': data.get('timezone', ''),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0)
                }
    except Exception as e:
        logger.warning(f"Failed to get location for IP {ip_address}: {e}")
    
    return {}


def cache_user_profile(user_id: int, profile_data: Dict) -> None:
    """
    Cache user profile data.
    """
    cache_key = f"user_profile_{user_id}"
    cache.set(cache_key, profile_data, timeout=3600)  # Cache for 1 hour


def get_cached_user_profile(user_id: int) -> Optional[Dict]:
    """
    Get cached user profile data.
    """
    cache_key = f"user_profile_{user_id}"
    return cache.get(cache_key)


def clear_user_profile_cache(user_id: int) -> None:
    """
    Clear cached user profile data.
    """
    cache_key = f"user_profile_{user_id}"
    cache.delete(cache_key)


def send_profile_completion_reminder(user_email: str, user_name: str, completion_percentage: float) -> bool:
    """
    Send email reminder for profile completion.
    """
    try:
        subject = 'Complete Your Profile - ClientNest'
        
        context = {
            'user_name': user_name,
            'completion_percentage': completion_percentage,
            'site_name': 'ClientNest'
        }
        
        html_message = render_to_string('profiles/emails/completion_reminder.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Profile completion reminder sent to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send profile completion reminder to {user_email}: {e}")
        return False


def export_user_profile_data(user) -> Dict[str, Any]:
    """
    Export all user profile data for GDPR compliance.
    """
    from .models import UserProfile, UserPreference, UserSkill, UserEducation, UserExperience
    
    data = {
        'user_info': {
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        },
        'profile': None,
        'preferences': None,
        'skills': [],
        'education': [],
        'experience': []
    }
    
    try:
        # Get profile data
        profile = UserProfile.objects.get(user=user)
        data['profile'] = {
            'bio': profile.bio,
            'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
            'gender': profile.gender,
            'phone_number': profile.phone_number,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'country': profile.country,
            'postal_code': profile.postal_code,
            'occupation': profile.occupation,
            'company': profile.company,
            'website': profile.website,
            'linkedin_url': profile.linkedin_url,
            'twitter_url': profile.twitter_url,
            'facebook_url': profile.facebook_url,
            'instagram_url': profile.instagram_url,
            'github_url': profile.github_url,
            'interests': profile.interests,
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat()
        }
    except UserProfile.DoesNotExist:
        pass
    
    try:
        # Get preferences
        preferences = UserPreference.objects.get(user=user)
        data['preferences'] = {
            'theme': preferences.theme,
            'language': preferences.language,
            'timezone': preferences.timezone,
            'email_notifications': preferences.email_notifications,
            'push_notifications': preferences.push_notifications,
            'sms_notifications': preferences.sms_notifications,
            'marketing_emails': preferences.marketing_emails,
            'profile_visibility': preferences.profile_visibility,
            'show_online_status': preferences.show_online_status,
            'allow_friend_requests': preferences.allow_friend_requests,
            'content_language': preferences.content_language,
            'show_mature_content': preferences.show_mature_content
        }
    except UserPreference.DoesNotExist:
        pass
    
    # Get skills
    skills = UserSkill.objects.filter(user=user)
    data['skills'] = [{
        'skill_name': skill.skill_name,
        'proficiency_level': skill.proficiency_level,
        'years_of_experience': skill.years_of_experience,
        'is_verified': skill.is_verified,
        'created_at': skill.created_at.isoformat()
    } for skill in skills]
    
    # Get education
    education = UserEducation.objects.filter(user=user)
    data['education'] = [{
        'institution_name': edu.institution_name,
        'degree_type': edu.degree_type,
        'field_of_study': edu.field_of_study,
        'start_date': edu.start_date.isoformat() if edu.start_date else None,
        'end_date': edu.end_date.isoformat() if edu.end_date else None,
        'gpa': str(edu.gpa) if edu.gpa else None,
        'description': edu.description
    } for edu in education]
    
    # Get experience
    experience = UserExperience.objects.filter(user=user)
    data['experience'] = [{
        'company_name': exp.company_name,
        'job_title': exp.job_title,
        'employment_type': exp.employment_type,
        'location': exp.location,
        'start_date': exp.start_date.isoformat() if exp.start_date else None,
        'end_date': exp.end_date.isoformat() if exp.end_date else None,
        'is_current': exp.is_current,
        'description': exp.description
    } for exp in experience]
    
    return data


def validate_image_upload(image_data: str) -> bool:
    """
    Validate base64 encoded image data.
    """
    try:
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
        # Check file size (max 5MB)
        if len(image_bytes) > 5 * 1024 * 1024:
            return False
        
        # Validate image format
        image = Image.open(BytesIO(image_bytes))
        
        # Check image dimensions (max 2048x2048)
        if image.width > 2048 or image.height > 2048:
            return False
        
        # Check format
        if image.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
            return False
        
        return True
        
    except Exception:
        return False


def log_profile_activity(user, activity_type: str, details: Dict = None):
    """
    Log profile-related activities.
    """
    from users.utils import log_user_activity
    
    log_user_activity(
        user=user,
        activity_type=f"profile_{activity_type}",
        details=details or {}
    )


def get_profile_analytics(user) -> Dict[str, Any]:
    """
    Get profile analytics and insights.
    """
    from .models import UserProfile, UserSkill, UserEducation, UserExperience
    
    analytics = {
        'profile_views': 0,  # TODO: Implement profile view tracking
        'profile_completion': 0,
        'skills_count': 0,
        'education_count': 0,
        'experience_count': 0,
        'last_updated': None,
        'account_age_days': 0
    }
    
    try:
        profile = UserProfile.objects.get(user=user)
        completion_data = calculate_profile_completion(profile)
        analytics['profile_completion'] = completion_data['overall_percentage']
        analytics['last_updated'] = profile.updated_at.isoformat()
    except UserProfile.DoesNotExist:
        pass
    
    analytics['skills_count'] = UserSkill.objects.filter(user=user).count()
    analytics['education_count'] = UserEducation.objects.filter(user=user).count()
    analytics['experience_count'] = UserExperience.objects.filter(user=user).count()
    
    if user.date_joined:
        analytics['account_age_days'] = (timezone.now() - user.date_joined).days
    
    return analytics