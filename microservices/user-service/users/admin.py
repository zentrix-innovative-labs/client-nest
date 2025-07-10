from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, UserActivity, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    
    list_display = (
        'email', 'username', 'get_full_name', 'is_verified', 'is_premium',
        'is_active', 'is_staff', 'created_at', 'last_login'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'is_verified', 'is_premium',
        'privacy_level', 'created_at', 'last_login'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login_ip')
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'bio', 'profile_picture',
                'phone_number', 'timezone', 'language'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_verified',
                'is_premium', 'groups', 'user_permissions'
            ),
        }),
        ('Privacy & Notifications', {
            'fields': (
                'privacy_level', 'email_notifications', 'push_notifications'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
        ('Security', {
            'fields': ('last_login_ip',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2', 'is_verified'
            ),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'Full Name'
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return '-'
    profile_picture_preview.short_description = 'Profile Picture'
    
    actions = ['verify_users', 'unverify_users', 'make_premium', 'remove_premium']
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            f'{updated} users were successfully verified.'
        )
    verify_users.short_description = 'Mark selected users as verified'
    
    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(
            request,
            f'{updated} users were successfully unverified.'
        )
    unverify_users.short_description = 'Mark selected users as unverified'
    
    def make_premium(self, request, queryset):
        updated = queryset.update(is_premium=True)
        self.message_user(
            request,
            f'{updated} users were successfully made premium.'
        )
    make_premium.short_description = 'Make selected users premium'
    
    def remove_premium(self, request, queryset):
        updated = queryset.update(is_premium=False)
        self.message_user(
            request,
            f'{updated} users had premium status removed.'
        )
    remove_premium.short_description = 'Remove premium from selected users'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """User Activity Admin"""
    
    list_display = (
        'user_email', 'activity_type', 'ip_address', 'timestamp'
    )
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__email', 'user__username', 'ip_address')
    readonly_fields = ('id', 'user', 'activity_type', 'ip_address', 'user_agent', 'timestamp', 'details')
    ordering = ('-timestamp',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """User Session Admin"""
    
    list_display = (
        'user_email', 'session_key_short', 'ip_address',
        'is_active', 'created_at', 'last_activity'
    )
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('user__email', 'user__username', 'session_key', 'ip_address')
    readonly_fields = (
        'id', 'user', 'session_key', 'ip_address', 'user_agent',
        'created_at', 'last_activity'
    )
    ordering = ('-last_activity',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def session_key_short(self, obj):
        return f"{obj.session_key[:8]}..."
    session_key_short.short_description = 'Session Key'
    
    actions = ['terminate_sessions']
    
    def terminate_sessions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} sessions were successfully terminated.'
        )
    terminate_sessions.short_description = 'Terminate selected sessions'
    
    def has_add_permission(self, request):
        return False