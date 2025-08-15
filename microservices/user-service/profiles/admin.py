from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile, UserPreference, UserSkill, 
    UserEducation, UserExperience
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile"""
    
    list_display = [
        'user_email', 'full_name', 'age', 'gender', 
        'city', 'country', 'completion_percentage', 'created_at'
    ]
    list_filter = [
        'gender', 'country', 'education_level', 
        'relationship_status', 'created_at', 'updated_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'city', 'country', 'occupation', 'company'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'age', 'completion_percentage']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'id')
        }),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'age', 'gender', 'phone_number',
                'relationship_status', 'bio_extended'
            )
        }),
        ('Address Information', {
            'fields': (
                'address_line_1', 'address_line_2', 'city',
                'state', 'postal_code', 'country'
            ),
            'classes': ('collapse',)
        }),
        ('Professional Information', {
            'fields': ('occupation', 'company', 'education_level'),
            'classes': ('collapse',)
        }),
        ('Social Media & Web Presence', {
            'fields': (
                'website', 'facebook_url', 'twitter_url',
                'linkedin_url', 'instagram_url', 'github_url'
            ),
            'classes': ('collapse',)
        }),
        ('Interests & Preferences', {
            'fields': ('interests',),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': (
                'show_email', 'show_phone', 'show_address', 'show_birth_date'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completion_percentage'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def full_name(self, obj):
        return obj.user.get_full_name() or 'N/A'
    full_name.short_description = 'Full Name'
    
    def completion_percentage(self, obj):
        percentage = obj.profile_completion_percentage()
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} %</span>',
            color, percentage
        )
    completion_percentage.short_description = 'Profile Completion'


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for UserPreference"""
    
    list_display = [
        'user_email', 'theme', 'language', 'timezone',
        'email_notifications', 'push_notifications', 'profile_visibility'
    ]
    list_filter = [
        'theme', 'language', 'email_notifications', 
        'push_notifications', 'profile_visibility', 'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'id')
        }),
        ('UI Preferences', {
            'fields': ('theme', 'language', 'timezone')
        }),
        ('Notification Preferences', {
            'fields': (
                'email_notifications', 'push_notifications',
                'sms_notifications', 'marketing_emails'
            )
        }),
        ('Privacy Preferences', {
            'fields': (
                'profile_visibility', 'show_online_status', 'allow_friend_requests'
            )
        }),
        ('Content Preferences', {
            'fields': ('content_language', 'mature_content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """Admin interface for UserSkill"""
    
    list_display = [
        'user_email', 'skill_name', 'proficiency_level_display',
        'years_of_experience', 'is_verified', 'created_at'
    ]
    list_filter = [
        'proficiency_level', 'is_verified', 'years_of_experience', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 'skill_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    actions = ['verify_skills', 'unverify_skills']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def proficiency_level_display(self, obj):
        colors = {
            1: 'red',
            2: 'orange', 
            3: 'blue',
            4: 'green',
            5: 'purple'
        }
        color = colors.get(obj.proficiency_level, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_proficiency_level_display()
        )
    proficiency_level_display.short_description = 'Proficiency'
    
    def verify_skills(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(
            request, 
            f'{updated} skill(s) were successfully verified.'
        )
    verify_skills.short_description = 'Verify selected skills'
    
    def unverify_skills(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(
            request, 
            f'{updated} skill(s) were successfully unverified.'
        )
    unverify_skills.short_description = 'Unverify selected skills'


@admin.register(UserEducation)
class UserEducationAdmin(admin.ModelAdmin):
    """Admin interface for UserEducation"""
    
    list_display = [
        'user_email', 'institution_name', 'degree_type',
        'field_of_study', 'start_date', 'end_date', 'is_current'
    ]
    list_filter = [
        'degree_type', 'is_current', 'start_date', 'end_date', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'institution_name', 'field_of_study'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'


@admin.register(UserExperience)
class UserExperienceAdmin(admin.ModelAdmin):
    """Admin interface for UserExperience"""
    
    list_display = [
        'user_email', 'company_name', 'job_title',
        'employment_type', 'start_date', 'end_date', 'is_current', 'duration_display'
    ]
    list_filter = [
        'employment_type', 'is_current', 'start_date', 'end_date', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'company_name', 'job_title', 'location'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'duration_display']
    date_hierarchy = 'start_date'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def duration_display(self, obj):
        return obj.duration
    duration_display.short_description = 'Duration'


# Inline admin classes for related models
class UserSkillInline(admin.TabularInline):
    model = UserSkill
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class UserEducationInline(admin.TabularInline):
    model = UserEducation
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class UserExperienceInline(admin.TabularInline):
    model = UserExperience
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    readonly_fields = ['created_at', 'updated_at', 'age']
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'gender', 'phone_number', 'bio_extended'
            )
        }),
        ('Address', {
            'fields': (
                'address_line_1', 'address_line_2', 'city',
                'state', 'postal_code', 'country'
            ),
            'classes': ('collapse',)
        }),
        ('Professional', {
            'fields': ('occupation', 'company', 'education_level'),
            'classes': ('collapse',)
        }),
    )