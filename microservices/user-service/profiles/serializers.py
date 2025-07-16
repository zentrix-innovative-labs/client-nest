from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    UserProfile, UserPreference, UserSkill,
    UserEducation, UserExperience
)

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    
    age = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    interests_list = serializers.ReadOnlyField()
    social_links = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        ref_name = "ProfilesUserProfile"
        
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_social_links(self, obj):
        """Get formatted social links"""
        return obj.get_social_links()
    
    def get_completion_percentage(self, obj):
        """Get profile completion percentage"""
        return obj.profile_completion_percentage()
    
    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        if value:
            from django.utils import timezone
            today = timezone.now().date()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            
            if age < 13:
                raise serializers.ValidationError("User must be at least 13 years old.")
            if age > 120:
                raise serializers.ValidationError("Please enter a valid date of birth.")
        
        return value


class UserProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating UserProfile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'date_of_birth', 'gender', 'phone_number',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'occupation', 'company',
            'education_level', 'relationship_status', 'website',
            'facebook_url', 'twitter_url', 'linkedin_url',
            'instagram_url', 'github_url', 'interests', 'bio_extended',
            'show_email', 'show_phone', 'show_address', 'show_birth_date'
        ]


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserPreference model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'user', 'user_email',
            'theme', 'language', 'timezone',
            'email_notifications', 'push_notifications', 'sms_notifications',
            'marketing_emails', 'profile_visibility', 'show_online_status',
            'allow_friend_requests', 'content_language', 'mature_content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserSkillSerializer(serializers.ModelSerializer):
    """Serializer for UserSkill model"""
    
    proficiency_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = [
            'id', 'user', 'user_email', 'skill_name',
            'proficiency_level', 'proficiency_display',
            'years_of_experience', 'is_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified', 'created_at', 'updated_at']
    
    def validate_skill_name(self, value):
        """Validate skill name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Skill name must be at least 2 characters long.")
        return value.strip().title()
    
    def validate_years_of_experience(self, value):
        """Validate years of experience"""
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value > 50:
            raise serializers.ValidationError("Years of experience seems too high.")
        return value


class UserEducationSerializer(serializers.ModelSerializer):
    """Serializer for UserEducation model"""
    
    degree_display = serializers.CharField(source='get_degree_type_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserEducation
        fields = [
            'id', 'user', 'user_email', 'institution_name',
            'degree_type', 'degree_display', 'field_of_study',
            'start_date', 'end_date', 'is_current', 'gpa',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate education data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        is_current = data.get('is_current', False)
        
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError("End date cannot be before start date.")
        
        if is_current and end_date:
            raise serializers.ValidationError("Current education cannot have an end date.")
        
        if not is_current and not end_date:
            raise serializers.ValidationError("Non-current education must have an end date.")
        
        return data
    
    def validate_gpa(self, value):
        """Validate GPA"""
        if value is not None and (value < 0.0 or value > 4.0):
            raise serializers.ValidationError("GPA must be between 0.0 and 4.0.")
        return value


class UserExperienceSerializer(serializers.ModelSerializer):
    """Serializer for UserExperience model"""
    
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    duration = serializers.ReadOnlyField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserExperience
        fields = [
            'id', 'user', 'user_email', 'company_name', 'job_title',
            'employment_type', 'employment_type_display', 'location',
            'start_date', 'end_date', 'is_current', 'description',
            'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate experience data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        is_current = data.get('is_current', False)
        
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError("End date cannot be before start date.")
        
        if is_current and end_date:
            raise serializers.ValidationError("Current position cannot have an end date.")
        
        if not is_current and not end_date:
            raise serializers.ValidationError("Non-current position must have an end date.")
        
        return data


class UserProfileSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for profile summary"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_email', 'user_name', 'occupation',
            'city', 'country', 'completion_percentage'
        ]
    
    def get_completion_percentage(self, obj):
        return obj.profile_completion_percentage()


class UserSkillSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for skill summary"""
    
    proficiency_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = ['skill_name', 'proficiency_level', 'proficiency_display', 'is_verified']


class UserEducationSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for education summary"""
    
    degree_display = serializers.CharField(source='get_degree_type_display', read_only=True)
    
    class Meta:
        model = UserEducation
        fields = ['institution_name', 'degree_type', 'degree_display', 'field_of_study']


class UserExperienceSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for experience summary"""
    
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    
    class Meta:
        model = UserExperience
        fields = ['company_name', 'job_title', 'employment_type_display', 'is_current']


class CompleteUserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile with all related data"""
    
    profile = UserProfileSerializer(read_only=True)
    preferences = UserPreferenceSerializer(read_only=True)
    skills = UserSkillSummarySerializer(many=True, read_only=True)
    education = UserEducationSummarySerializer(many=True, read_only=True)
    experience = UserExperienceSummarySerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_verified', 'is_premium', 'profile', 'preferences',
            'skills', 'education', 'experience'
        ]
        read_only_fields = ['id', 'email', 'username', 'is_verified', 'is_premium']