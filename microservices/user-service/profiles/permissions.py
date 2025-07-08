from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsProfileOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the profile.
    """
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class CanViewProfile(permissions.BasePermission):
    """
    Permission to check if user can view a profile based on privacy settings.
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always view their own profile
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Check profile visibility settings
        if hasattr(obj, 'profile_visibility'):
            if obj.profile_visibility == 'public':
                return True
            elif obj.profile_visibility == 'private':
                return False
            elif obj.profile_visibility == 'friends':
                # TODO: Implement friends relationship check
                return False
        
        # Default to public if no visibility setting
        return True


class CanModifyProfile(permissions.BasePermission):
    """
    Permission to check if user can modify profile data.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Only owner can modify their profile
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission to check if user is verified.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'is_verified', False)
        )


class IsPremiumUser(permissions.BasePermission):
    """
    Permission to check if user has premium access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'is_premium', False)
        )


class CanAccessAdvancedFeatures(permissions.BasePermission):
    """
    Permission for advanced profile features (premium or verified users).
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        return (
            getattr(request.user, 'is_premium', False) or 
            getattr(request.user, 'is_verified', False)
        )


class RateLimitPermission(permissions.BasePermission):
    """
    Custom permission to implement rate limiting.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True
        
        # Check for recent profile updates (max 10 per hour)
        from .models import UserProfile
        recent_updates = UserProfile.objects.filter(
            user=request.user,
            updated_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        if request.method in ['POST', 'PUT', 'PATCH'] and recent_updates >= 10:
            return False
        
        return True


class CanManageSkills(permissions.BasePermission):
    """
    Permission to manage skills (with rate limiting).
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Rate limit skill creation (max 20 skills per day)
        if request.method == 'POST':
            from .models import UserSkill
            today_skills = UserSkill.objects.filter(
                user=request.user,
                created_at__date=timezone.now().date()
            ).count()
            
            if today_skills >= 20:
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanManageEducation(permissions.BasePermission):
    """
    Permission to manage education records.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanManageExperience(permissions.BasePermission):
    """
    Permission to manage work experience records.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission for admin users or object owners.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class CanViewPrivateInfo(permissions.BasePermission):
    """
    Permission to view private profile information.
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always view their private info
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Admin can view private info
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user has permission to view private info
        # (e.g., through friendship, premium features, etc.)
        return False


class CanExportData(permissions.BasePermission):
    """
    Permission to export profile data.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and
            getattr(request.user, 'is_verified', False)
        )
    
    def has_object_permission(self, request, view, obj):
        # Users can only export their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user