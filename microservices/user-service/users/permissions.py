from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to allow access to admins or object owners.
    """
    
    def has_permission(self, request, view):
        # Allow authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow admin users full access
        if request.user.is_staff:
            return True
        
        # Allow owners to access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For User objects, check if it's the same user
        return obj == request.user


class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow verified users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsPremiumUser(permissions.BasePermission):
    """
    Custom permission to only allow premium users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_premium
        )


class IsActiveUser(permissions.BasePermission):
    """
    Custom permission to only allow active users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )


class CanViewProfile(permissions.BasePermission):
    """
    Custom permission for viewing user profiles based on privacy settings.
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always view their own profile
        if obj == request.user:
            return True
        
        # Admin can view all profiles
        if request.user.is_staff:
            return True
        
        # Check privacy level
        if obj.privacy_level == 'public':
            return True
        elif obj.privacy_level == 'friends':
            # TODO: Implement friend relationship check
            return False
        elif obj.privacy_level == 'private':
            return False
        
        return False


class CanModifyProfile(permissions.BasePermission):
    """
    Custom permission for modifying user profiles.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only the owner can modify their profile
        if obj == request.user:
            return True
        
        # Admin can modify profiles
        if request.user.is_staff:
            return True
        
        return False


class IsServiceAccount(permissions.BasePermission):
    """
    Custom permission for service-to-service communication.
    """
    
    def has_permission(self, request, view):
        # Check for service account token or API key
        service_token = request.META.get('HTTP_X_SERVICE_TOKEN')
        api_key = request.META.get('HTTP_X_API_KEY')
        
        # TODO: Implement proper service account validation
        # For now, just check if the headers exist
        return service_token or api_key


class RateLimitPermission(permissions.BasePermission):
    """
    Custom permission to implement rate limiting.
    """
    
    def has_permission(self, request, view):
        # TODO: Implement rate limiting logic
        # This could check Redis for request counts per user/IP
        return True