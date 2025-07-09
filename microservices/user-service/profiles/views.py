from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import (
    UserProfile, UserPreference, UserSkill,
    UserEducation, UserExperience
)
from .serializers import (
    UserProfileSerializer, UserProfileCreateSerializer,
    UserPreferenceSerializer, UserSkillSerializer,
    UserEducationSerializer, UserExperienceSerializer,
    CompleteUserProfileSerializer, UserProfileSummarySerializer
)
from users.permissions import IsOwnerOrReadOnly, IsAdminOrOwner
from users.utils import log_user_activity, get_client_ip
from .utils import (
    calculate_profile_completion, 
    log_profile_activity,
    validate_social_url,
    validate_phone_number,
    validate_skill_name,
    export_user_profile_data,
    get_profile_analytics,
    generate_username_suggestions
)

User = get_user_model()


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'country', 'education_level', 'relationship_status']
    search_fields = ['user__first_name', 'user__last_name', 'occupation', 'company', 'city']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        if self.request.user.is_staff:
            return UserProfile.objects.all().select_related('user')
        return UserProfile.objects.filter(user=self.request.user).select_related('user')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return UserProfileCreateSerializer
        elif self.action == 'list':
            return UserProfileSummarySerializer
        return UserProfileSerializer
    
    def perform_create(self, serializer):
        """Create profile for authenticated user"""
        profile = serializer.save(user=self.request.user)
        log_user_activity(
            user=self.request.user,
            activity_type='profile_created',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={'profile_id': str(profile.id)}
        )
    
    def perform_update(self, serializer):
        """Update profile and log activity"""
        old_completion = serializer.instance.profile_completion_percentage()
        profile = serializer.save()
        new_completion = profile.profile_completion_percentage()
        
        log_user_activity(
            user=self.request.user,
            activity_type='profile_updated',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'profile_id': str(profile.id),
                'completion_change': new_completion - old_completion
            }
        )
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found. Please create a profile first.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def create_profile(self, request):
        """Create profile for current user"""
        if UserProfile.objects.filter(user=request.user).exists():
            return Response(
                {'detail': 'Profile already exists. Use PUT to update.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserProfileCreateSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save(user=request.user)
            response_serializer = UserProfileSerializer(profile)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def completion_stats(self, request, pk=None):
        """Get profile completion statistics"""
        profile = self.get_object()
        
        # Calculate field completion
        fields_to_check = [
            'date_of_birth', 'gender', 'phone_number', 'address_line_1',
            'city', 'country', 'occupation', 'bio_extended'
        ]
        
        completed_fields = []
        missing_fields = []
        
        for field in fields_to_check:
            if getattr(profile, field):
                completed_fields.append(field)
            else:
                missing_fields.append(field)
        
        return Response({
            'completion_percentage': profile.profile_completion_percentage(),
            'completed_fields': completed_fields,
            'missing_fields': missing_fields,
            'total_fields': len(fields_to_check)
        })


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user preferences"""
    
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        if self.request.user.is_staff:
            return UserPreference.objects.all().select_related('user')
        return UserPreference.objects.filter(user=self.request.user).select_related('user')
    
    def perform_create(self, serializer):
        """Create preferences for authenticated user"""
        preferences = serializer.save(user=self.request.user)
        log_user_activity(
            user=self.request.user,
            activity_type='preferences_created',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={'preferences_id': str(preferences.id)}
        )
    
    def perform_update(self, serializer):
        """Update preferences and log activity"""
        preferences = serializer.save()
        log_user_activity(
            user=self.request.user,
            activity_type='preferences_updated',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={'preferences_id': str(preferences.id)}
        )
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get current user's preferences"""
        try:
            preferences = UserPreference.objects.get(user=request.user)
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        except UserPreference.DoesNotExist:
            return Response(
                {'detail': 'Preferences not found. Please create preferences first.'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserSkillViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user skills"""
    
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['proficiency_level', 'is_verified', 'years_of_experience']
    search_fields = ['skill_name']
    ordering_fields = ['proficiency_level', 'years_of_experience', 'created_at']
    ordering = ['-proficiency_level', 'skill_name']
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        if self.request.user.is_staff:
            return UserSkill.objects.all().select_related('user')
        return UserSkill.objects.filter(user=self.request.user).select_related('user')
    
    def perform_create(self, serializer):
        """Create skill for authenticated user"""
        skill = serializer.save(user=self.request.user)
        log_user_activity(
            user=self.request.user,
            activity_type='skill_added',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'skill_id': str(skill.id),
                'skill_name': skill.skill_name,
                'proficiency_level': skill.proficiency_level
            }
        )
    
    @action(detail=False, methods=['get'])
    def my_skills(self, request):
        """Get current user's skills"""
        skills = UserSkill.objects.filter(user=request.user)
        serializer = self.get_serializer(skills, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def skill_summary(self, request):
        """Get skill summary statistics"""
        skills = UserSkill.objects.filter(user=request.user)
        
        summary = {
            'total_skills': skills.count(),
            'verified_skills': skills.filter(is_verified=True).count(),
            'proficiency_breakdown': {},
            'top_skills': []
        }
        
        # Proficiency breakdown
        for level in range(1, 6):
            count = skills.filter(proficiency_level=level).count()
            level_name = dict(UserSkill.PROFICIENCY_CHOICES)[level]
            summary['proficiency_breakdown'][level_name] = count
        
        # Top skills (highest proficiency)
        top_skills = skills.filter(proficiency_level__gte=4).order_by('-proficiency_level', 'skill_name')[:5]
        summary['top_skills'] = UserSkillSerializer(top_skills, many=True).data
        
        return Response(summary)


class UserEducationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user education"""
    
    serializer_class = UserEducationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['degree_type', 'is_current']
    search_fields = ['institution_name', 'field_of_study']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        if self.request.user.is_staff:
            return UserEducation.objects.all().select_related('user')
        return UserEducation.objects.filter(user=self.request.user).select_related('user')
    
    def perform_create(self, serializer):
        """Create education for authenticated user"""
        education = serializer.save(user=self.request.user)
        log_user_activity(
            user=self.request.user,
            activity_type='education_added',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'education_id': str(education.id),
                'institution': education.institution_name,
                'degree': education.degree_type
            }
        )
    
    @action(detail=False, methods=['get'])
    def my_education(self, request):
        """Get current user's education"""
        education = UserEducation.objects.filter(user=request.user)
        serializer = self.get_serializer(education, many=True)
        return Response(serializer.data)


class UserExperienceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user experience"""
    
    serializer_class = UserExperienceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employment_type', 'is_current']
    search_fields = ['company_name', 'job_title', 'location']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        if self.request.user.is_staff:
            return UserExperience.objects.all().select_related('user')
        return UserExperience.objects.filter(user=self.request.user).select_related('user')
    
    def perform_create(self, serializer):
        """Create experience for authenticated user"""
        experience = serializer.save(user=self.request.user)
        log_user_activity(
            user=self.request.user,
            activity_type='experience_added',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'experience_id': str(experience.id),
                'company': experience.company_name,
                'position': experience.job_title
            }
        )
    
    @action(detail=False, methods=['get'])
    def my_experience(self, request):
        """Get current user's experience"""
        experience = UserExperience.objects.filter(user=request.user)
        serializer = self.get_serializer(experience, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def career_summary(self, request):
        """Get career summary statistics"""
        experiences = UserExperience.objects.filter(user=request.user)
        
        summary = {
            'total_positions': experiences.count(),
            'current_positions': experiences.filter(is_current=True).count(),
            'companies_worked': experiences.values('company_name').distinct().count(),
            'employment_types': {},
            'recent_experience': []
        }
        
        # Employment type breakdown
        for emp_type, display_name in UserExperience.EMPLOYMENT_TYPE_CHOICES:
            count = experiences.filter(employment_type=emp_type).count()
            summary['employment_types'][display_name] = count
        
        # Recent experience (last 3 positions)
        recent = experiences.order_by('-start_date')[:3]
        summary['recent_experience'] = UserExperienceSerializer(recent, many=True).data
        
        return Response(summary)


class CompleteProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for getting complete user profiles"""
    
    serializer_class = CompleteUserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']
    
    def get_queryset(self):
        """Get queryset with all related data"""
        queryset = User.objects.select_related(
            'profile', 'preferences'
        ).prefetch_related(
            'skills', 'education', 'experience'
        )
        
        if not self.request.user.is_staff:
            # Non-staff users can only see their own complete profile
            queryset = queryset.filter(id=self.request.user.id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_complete_profile(self, request):
        """Get current user's complete profile"""
        user = get_object_or_404(User, id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create_profile(self, request):
        """Create complete profile in one transaction"""
        try:
            with transaction.atomic():
                # Create or update profile
                profile_data = request.data.get('profile', {})
                if profile_data:
                    profile, created = UserProfile.objects.get_or_create(
                        user=request.user,
                        defaults=profile_data
                    )
                    if not created:
                        for key, value in profile_data.items():
                            setattr(profile, key, value)
                        profile.save()
                
                # Create or update preferences
                preferences_data = request.data.get('preferences', {})
                if preferences_data:
                    preferences, created = UserPreference.objects.get_or_create(
                        user=request.user,
                        defaults=preferences_data
                    )
                    if not created:
                        for key, value in preferences_data.items():
                            setattr(preferences, key, value)
                        preferences.save()
                
                # Add skills
                skills_data = request.data.get('skills', [])
                for skill_data in skills_data:
                    UserSkill.objects.get_or_create(
                        user=request.user,
                        skill_name=skill_data['skill_name'],
                        defaults=skill_data
                    )
                
                # Add education
                education_data = request.data.get('education', [])
                for edu_data in education_data:
                    UserEducation.objects.create(
                        user=request.user,
                        **edu_data
                    )
                
                # Add experience
                experience_data = request.data.get('experience', [])
                for exp_data in experience_data:
                    UserExperience.objects.create(
                        user=request.user,
                        **exp_data
                    )
                
                # Log activity
                log_user_activity(
                    user=request.user,
                    activity_type='bulk_profile_created',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details={'sections_created': list(request.data.keys())}
                )
                
                # Return complete profile
                user = User.objects.select_related(
                    'profile', 'preferences'
                ).prefetch_related(
                    'skills', 'education', 'experience'
                ).get(id=request.user.id)
                
                serializer = CompleteUserProfileSerializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'detail': f'Error creating profile: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ExportProfileDataView(viewsets.GenericViewSet):
    """
    Export user profile data for GDPR compliance.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """
        Export all user profile data.
        """
        try:
            exported_data = export_user_profile_data(request.user)
            
            # Log the export activity
            log_user_activity(
                user=request.user,
                activity_type='data_exported',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'export_timestamp': str(request.user.date_joined)}
            )
            
            return Response(exported_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to export profile data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidateSocialURLView(viewsets.GenericViewSet):
    """
    Validate social media URLs.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def validate_url(self, request):
        """
        Validate a social media URL.
        """
        url = request.data.get('url')
        platform = request.data.get('platform')
        
        if not url or not platform:
            return Response(
                {'error': 'URL and platform are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_valid = validate_social_url(url, platform)
        
        return Response({
            'is_valid': is_valid,
            'url': url,
            'platform': platform
        }, status=status.HTTP_200_OK)


class ValidatePhoneView(viewsets.GenericViewSet):
    """
    Validate phone numbers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def validate_phone(self, request):
        """
        Validate a phone number.
        """
        phone = request.data.get('phone')
        country_code = request.data.get('country_code')
        
        if not phone:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_valid = validate_phone_number(phone, country_code)
        
        return Response({
            'is_valid': is_valid,
            'phone': phone,
            'country_code': country_code
        }, status=status.HTTP_200_OK)


class ValidateSkillView(viewsets.GenericViewSet):
    """
    Validate skill names.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def validate_skill(self, request):
        """
        Validate a skill name.
        """
        skill_name = request.data.get('skill_name')
        
        if not skill_name:
            return Response(
                {'error': 'Skill name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_valid = validate_skill_name(skill_name)
        
        return Response({
            'is_valid': is_valid,
            'skill_name': skill_name,
            'normalized_name': skill_name.strip().title() if is_valid else None
        }, status=status.HTTP_200_OK)


class ProfileAnalyticsView(viewsets.GenericViewSet):
    """
    Get profile analytics and insights.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def get_analytics(self, request):
        """
        Get profile analytics for the current user.
        """
        try:
            analytics = get_profile_analytics(request.user)
            
            return Response(analytics, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to get profile analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UsernameSuggestionsView(viewsets.GenericViewSet):
    """
    Generate username suggestions.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate_suggestions(self, request):
        """
        Generate username suggestions based on user input.
        """
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        email = request.data.get('email', '')
        
        if not any([first_name, last_name, email]):
            return Response(
                {'error': 'At least one of first_name, last_name, or email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            suggestions = generate_username_suggestions(first_name, last_name, email)
            
            return Response({
                'suggestions': suggestions,
                'count': len(suggestions)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to generate username suggestions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )