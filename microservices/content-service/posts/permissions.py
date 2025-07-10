from rest_framework import permissions

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
        return obj.user == request.user

class IsPostOwner(permissions.BasePermission):
    """
    Permission to check if user owns the post
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user owns the post
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'post'):
            return obj.post.user == request.user
        return False

class IsSocialAccountOwner(permissions.BasePermission):
    """
    Permission to check if user owns the social account
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CanManagePost(permissions.BasePermission):
    """
    Permission to check if user can manage the post (edit, delete, publish)
    """
    
    def has_object_permission(self, request, view, obj):
        # Only the post owner can manage it
        if obj.user != request.user:
            return False
        
        # Additional checks based on post status
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Cannot edit published posts (except metadata)
            if obj.status == 'published' and view.action not in ['partial_update']:
                return False
        
        return True

class CanPublishPost(permissions.BasePermission):
    """
    Permission to check if user can publish posts
    """
    
    def has_object_permission(self, request, view, obj):
        # Only the post owner can publish
        if obj.user != request.user:
            return False
        
        # Check if user has active social accounts
        if not obj.user.social_accounts.filter(is_active=True).exists():
            return False
        
        return True