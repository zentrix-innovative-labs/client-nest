from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class CanViewAnalytics(permissions.BasePermission):
    """
    Permission to view analytics data.
    Users can view their own analytics or analytics they have access to.
    """
    
    def has_permission(self, request, view):
        """Check if user can view analytics"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can view specific analytics object"""
        # Check based on object type
        if hasattr(obj, 'user'):
            # For UserAnalytics, PlatformAnalytics, etc.
            return obj.user == request.user
        
        if hasattr(obj, 'post'):
            # For PostAnalytics
            return obj.post.owner == request.user
        
        if hasattr(obj, 'shared_with'):
            # For AnalyticsReport
            return (
                obj.user == request.user or
                request.user in obj.shared_with.all() or
                obj.is_public
            )
        
        # Default: check if user owns the object
        return getattr(obj, 'user', None) == request.user

class CanManageAnalytics(permissions.BasePermission):
    """
    Permission to manage (create, update, delete) analytics data.
    Only owners can manage their analytics.
    """
    
    def has_permission(self, request, view):
        """Check if user can manage analytics"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage specific analytics object"""
        # Only owners can manage analytics
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'post'):
            return obj.post.owner == request.user
        
        # Default: check if user owns the object
        return getattr(obj, 'user', None) == request.user

class CanExportAnalytics(permissions.BasePermission):
    """
    Permission to export analytics data.
    Users can export their own analytics with rate limiting.
    """
    
    def has_permission(self, request, view):
        """Check if user can export analytics"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check export rate limit (max 10 exports per day)
        today = timezone.now().date()
        from .models import AnalyticsReport
        
        daily_exports = AnalyticsReport.objects.filter(
            user=request.user,
            report_type='export',
            created_at__date=today
        ).count()
        
        return daily_exports < 10
    
    def has_object_permission(self, request, view, obj):
        """Check if user can export specific analytics object"""
        # Check ownership
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'post'):
            return obj.post.owner == request.user
        
        return getattr(obj, 'user', None) == request.user

class CanCreateReports(permissions.BasePermission):
    """
    Permission to create analytics reports.
    Users can create reports for their own data with limits.
    """
    
    def has_permission(self, request, view):
        """Check if user can create reports"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check report creation limit (max 50 reports per user)
        from .models import AnalyticsReport
        
        user_reports = AnalyticsReport.objects.filter(
            user=request.user
        ).count()
        
        return user_reports < 50
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage specific report"""
        return obj.user == request.user

class CanShareReports(permissions.BasePermission):
    """
    Permission to share analytics reports.
    Only report owners can share their reports.
    """
    
    def has_permission(self, request, view):
        """Check if user can share reports"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can share specific report"""
        return obj.user == request.user

class CanAccessSharedReport(permissions.BasePermission):
    """
    Permission to access shared analytics reports.
    Users can access reports shared with them or public reports.
    """
    
    def has_permission(self, request, view):
        """Check if user can access shared reports"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access specific shared report"""
        return (
            obj.user == request.user or
            request.user in obj.shared_with.all() or
            obj.is_public
        )

class CanViewInsights(permissions.BasePermission):
    """
    Permission to view analytics insights.
    Users can view insights generated for their data.
    """
    
    def has_permission(self, request, view):
        """Check if user can view insights"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can view specific insight"""
        return obj.user == request.user

class CanManageInsights(permissions.BasePermission):
    """
    Permission to manage analytics insights.
    Users can dismiss or mark actions on their insights.
    """
    
    def has_permission(self, request, view):
        """Check if user can manage insights"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage specific insight"""
        return obj.user == request.user

class CanAccessDashboard(permissions.BasePermission):
    """
    Permission to access analytics dashboard.
    Authenticated users can access their own dashboard.
    """
    
    def has_permission(self, request, view):
        """Check if user can access dashboard"""
        return request.user and request.user.is_authenticated

class CanSyncAnalytics(permissions.BasePermission):
    """
    Permission to sync analytics data from platforms.
    Users can sync their own analytics with rate limiting.
    """
    
    def has_permission(self, request, view):
        """Check if user can sync analytics"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check sync rate limit (max 20 syncs per hour)
        hour_ago = timezone.now() - timedelta(hours=1)
        
        # Check recent sync requests (you might want to track this in a model)
        # For now, we'll allow all authenticated users
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user can sync specific analytics object"""
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'post'):
            return obj.post.owner == request.user
        
        return getattr(obj, 'user', None) == request.user

class CanBulkManageAnalytics(permissions.BasePermission):
    """
    Permission to perform bulk operations on analytics.
    Users can bulk manage their own analytics with limits.
    """
    
    def has_permission(self, request, view):
        """Check if user can perform bulk operations"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check bulk operation limits
        if request.method == 'POST':
            data = request.data
            
            # Limit bulk operations to 100 items at a time
            post_ids = data.get('post_ids', [])
            if len(post_ids) > 100:
                return False
        
        return True

class CanAccessTeamAnalytics(permissions.BasePermission):
    """
    Permission to access team analytics.
    Team members can view aggregated team analytics.
    """
    
    def has_permission(self, request, view):
        """Check if user can access team analytics"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user is part of any team
        # This would depend on your team model implementation
        # For now, we'll allow all authenticated users
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access specific team analytics"""
        # Check if user is part of the team
        # This would depend on your team model implementation
        return True

class CanGenerateInsights(permissions.BasePermission):
    """
    Permission to generate analytics insights.
    Users can generate insights for their data with rate limiting.
    """
    
    def has_permission(self, request, view):
        """Check if user can generate insights"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check insight generation rate limit (max 5 per day)
        today = timezone.now().date()
        from .models import AnalyticsInsight
        
        daily_insights = AnalyticsInsight.objects.filter(
            user=request.user,
            created_at__date=today
        ).count()
        
        return daily_insights < 5

class CanScheduleReports(permissions.BasePermission):
    """
    Permission to schedule analytics reports.
    Users can schedule reports for their data with limits.
    """
    
    def has_permission(self, request, view):
        """Check if user can schedule reports"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check scheduled report limit (max 10 scheduled reports per user)
        from .models import AnalyticsReport
        
        scheduled_reports = AnalyticsReport.objects.filter(
            user=request.user,
            is_scheduled=True,
            status__in=['pending', 'processing']
        ).count()
        
        return scheduled_reports < 10
    
    def has_object_permission(self, request, view, obj):
        """Check if user can schedule specific report"""
        return obj.user == request.user

class IsAnalyticsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows owners to edit analytics,
    but read-only access for others with view permission.
    """
    
    def has_permission(self, request, view):
        """Check if user has basic permission"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission"""
        # Read permissions for any authenticated user with view access
        if request.method in permissions.SAFE_METHODS:
            # Check if user can view this analytics object
            if hasattr(obj, 'user'):
                return (
                    obj.user == request.user or
                    getattr(obj, 'is_public', False)
                )
            
            if hasattr(obj, 'post'):
                return obj.post.owner == request.user
            
            if hasattr(obj, 'shared_with'):
                return (
                    obj.user == request.user or
                    request.user in obj.shared_with.all() or
                    getattr(obj, 'is_public', False)
                )
        
        # Write permissions only for owners
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'post'):
            return obj.post.owner == request.user
        
        return getattr(obj, 'user', None) == request.user

class CanAccessAnalyticsAPI(permissions.BasePermission):
    """
    Base permission for analytics API access.
    Ensures user is authenticated and has basic analytics access.
    """
    
    def has_permission(self, request, view):
        """Check if user can access analytics API"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user has any posts or analytics data
        from posts.models import Post
        
        has_posts = Post.objects.filter(owner=request.user).exists()
        
        # Users with posts can access analytics
        return has_posts