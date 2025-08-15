from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView, UserProfileView,
    UserViewSet, ChangePasswordView, PasswordResetView, PasswordResetConfirmView,
    EmailVerificationView, ResendVerificationView, UserActivityViewSet,
    UserSessionViewSet
)


# Create router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'activities', UserActivityViewSet, basename='activity')
router.register(r'sessions', UserSessionViewSet, basename='session')

# URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # Password management
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/reset-password/', PasswordResetView.as_view(), name='password-reset'),
    path('auth/reset-password/<str:uidb64>/<str:token>/', 
         PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Email verification
    path('auth/verify-email/<str:uidb64>/<str:token>/', 
         EmailVerificationView.as_view(), name='email-verify'),
    path('auth/resend-verification/', 
         ResendVerificationView.as_view(), name='resend-verification'),
    
    # Include router URLs
    path('', include(router.urls)),
]

# Add URL names for easier reference
app_name = 'users'