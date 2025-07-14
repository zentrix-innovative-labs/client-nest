from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'preferences', views.UserPreferenceViewSet, basename='userpreference')
router.register(r'skills', views.UserSkillViewSet, basename='userskill')
router.register(r'education', views.UserEducationViewSet, basename='usereducation')
router.register(r'experience', views.UserExperienceViewSet, basename='userexperience')
router.register(r'complete-profile', views.CompleteProfileViewSet, basename='completeprofile')

app_name = 'profiles'

urlpatterns = [
    # Profile management endpoints
    path('my-profile/', views.UserProfileViewSet.as_view({
        'get': 'my_profile',
        'post': 'create_profile',
        'put': 'update',
        'patch': 'partial_update'
    }), name='my-profile'),
    
    path('my-preferences/', views.UserPreferenceViewSet.as_view({
        'get': 'my_preferences',
        'put': 'update',
        'patch': 'partial_update'
    }), name='my-preferences'),
    
    path('my-skills/', views.UserSkillViewSet.as_view({
        'get': 'my_skills',
        'post': 'create'
    }), name='my-skills'),
    
    path('my-education/', views.UserEducationViewSet.as_view({
        'get': 'my_education',
        'post': 'create'
    }), name='my-education'),
    
    path('my-experience/', views.UserExperienceViewSet.as_view({
        'get': 'my_experience',
        'post': 'create'
    }), name='my-experience'),
    
    # Profile statistics and analytics
    path('completion-stats/', views.UserProfileViewSet.as_view({
        'get': 'completion_stats'
    }), name='completion-stats'),
    
    path('skill-summary/', views.UserSkillViewSet.as_view({
        'get': 'skill_summary'
    }), name='skill-summary'),
    
    path('career-summary/', views.UserExperienceViewSet.as_view({
        'get': 'career_summary'
    }), name='career-summary'),
    
    # Complete profile operations
    path('complete-profile/me/', views.CompleteProfileViewSet.as_view({
        'get': 'retrieve'
    }), name='complete-profile-me'),
    
    path('complete-profile/bulk-create/', views.CompleteProfileViewSet.as_view({
        'post': 'bulk_create'
    }), name='complete-profile-bulk-create'),
    
    # Profile export (GDPR compliance)
    path('export-data/', views.ExportProfileDataView.as_view({'get': 'export_data'}), name='export-data'),
    
    # Profile validation endpoints
    path('validate-social-url/', views.ValidateSocialURLView.as_view({'post': 'validate_url'}), name='validate-social-url'),
    path('validate-phone/', views.ValidatePhoneView.as_view({'post': 'validate_phone'}), name='validate-phone'),
    path('validate-skill/', views.ValidateSkillView.as_view({'post': 'validate_skill'}), name='validate-skill'),
    
    # Profile analytics
    path('analytics/', views.ProfileAnalyticsView.as_view({'get': 'get_analytics'}), name='analytics'),
    
    # Username suggestions
    path('username-suggestions/', views.UsernameSuggestionsView.as_view({'get': 'get_suggestions'}), name='username-suggestions'),
    
    # Include router URLs
    path('', include(router.urls)),
]