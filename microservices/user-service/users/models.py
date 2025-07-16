from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    
    # Override email to make it unique and required
    email = models.EmailField(
        unique=True,
        help_text='Required. Enter a valid email address.'
    )
    
    # Additional user fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text='Upload a profile picture'
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        help_text='Phone number in international format'
    )
    
    # Account status fields
    is_verified = models.BooleanField(
        default=False,
        help_text='Designates whether this user has verified their email address.'
    )
    is_premium = models.BooleanField(
        default=False,
        help_text='Designates whether this user has a premium subscription.'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Privacy settings
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends', 'Friends Only'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text='Receive email notifications'
    )
    push_notifications = models.BooleanField(
        default=True,
        help_text='Receive push notifications'
    )
    
    # Account settings
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text='User timezone'
    )
    language = models.CharField(
        max_length=10,
        default='en',
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
        ]
    )
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username
    
    @property
    def is_profile_complete(self):
        """Check if user profile is complete"""
        required_fields = [self.first_name, self.last_name, self.email]
        return all(field for field in required_fields)
    
    def soft_delete(self):
        """Soft delete user by deactivating account"""
        self.is_active = False
        self.email = f"deleted_{self.id}@deleted.com"
        self.username = f"deleted_{self.id}"
        self.save()
    
    def update_last_login_ip(self, ip_address):
        """Update the last login IP address"""
        self.last_login_ip = ip_address
        self.save(update_fields=['last_login_ip'])


class UserActivity(models.Model):
    """Track user activity for analytics and security"""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('email_verification', 'Email Verification'),
        ('account_deactivation', 'Account Deactivation'),
        ('failed_login', 'Failed Login'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'users_activity'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} at {self.timestamp}"


class UserSession(models.Model):
    """Track active user sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'users_session'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - Session {self.session_key[:8]}..."
    
    def is_expired(self, timeout_minutes=30):
        """Check if session is expired"""
        from datetime import timedelta
        expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
        return timezone.now() > expiry_time
    
    def terminate(self):
        """Terminate the session"""
        self.is_active = False
        self.save()