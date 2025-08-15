from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import logging

from .models import User, UserActivity, UserSession
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserListSerializer, ChangePasswordSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, UserActivitySerializer, UserSessionSerializer,
    EmailVerificationSerializer, ResendVerificationSerializer, UserStatsSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrOwner
from .utils import get_client_ip, log_user_activity, send_verification_email

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log registration activity
        log_user_activity(
            user=user,
            activity_type='registration',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'registration_method': 'email'}
        )
        
        # Send verification email
        send_verification_email(user, request)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful. Please check your email for verification.'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(TokenObtainPairView):
    """User login endpoint"""
    
    serializer_class = UserLoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last login IP
        user.update_last_login_ip(get_client_ip(request))
        
        # Log login activity
        log_user_activity(
            user=user,
            activity_type='login',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'login_method': 'email'}
        )
        
        # Create or update session
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.update_or_create(
                user=user,
                session_key=session_key,
                defaults={
                    'ip_address': get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'last_activity': timezone.now(),
                    'is_active': True
                }
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        })


class UserLogoutView(APIView):
    """User logout endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Deactivate session
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(
                    user=request.user,
                    session_key=session_key
                ).update(is_active=False)
            
            # Log logout activity
            log_user_activity(
                user=request.user,
                activity_type='logout',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logout(request)
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view and update"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        # Log profile update activity
        log_user_activity(
            user=request.user,
            activity_type='profile_update',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'updated_fields': list(request.data.keys())}
        )
        
        return response


class UserViewSet(ModelViewSet):
    """User management viewset for admin"""
    
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_verified', 'is_premium', 'privacy_level']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'last_login', 'email']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserProfileSerializer
        return UserListSerializer
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a user"""
        user = self.get_object()
        user.is_verified = True
        user.save()
        
        log_user_activity(
            user=user,
            activity_type='admin_verification',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'verified_by': request.user.email}
        )
        
        return Response({'message': 'User verified successfully'})
    
    @action(detail=True, methods=['post'])
    def make_premium(self, request, pk=None):
        """Make user premium"""
        user = self.get_object()
        user.is_premium = True
        user.save()
        
        log_user_activity(
            user=user,
            activity_type='premium_granted',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'granted_by': request.user.email}
        )
        
        return Response({'message': 'User made premium successfully'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        stats = {
            'total_users': User.objects.count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'premium_users': User.objects.filter(is_premium=True).count(),
            'active_sessions': UserSession.objects.filter(
                is_active=True,
                last_activity__gte=timezone.now() - timedelta(hours=24)
            ).count(),
            'recent_activities': UserActivity.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24)
            ).count()
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    """Change password endpoint"""
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log password change activity
        log_user_activity(
            user=request.user,
            activity_type='password_change',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': 'Password changed successfully'
        })


class PasswordResetView(generics.GenericAPIView):
    """Password reset request endpoint"""
    
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email, is_active=True)
        
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Send reset email
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        send_mail(
            subject='Password Reset Request',
            message=f'Click the link to reset your password: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        # Log password reset request
        log_user_activity(
            user=user,
            activity_type='password_reset_request',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': 'Password reset email sent successfully'
        })


class PasswordResetConfirmView(generics.GenericAPIView):
    """Password reset confirmation endpoint"""
    
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Invalid reset link'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({
                'error': 'Invalid or expired reset link'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log password reset completion
        log_user_activity(
            user=user,
            activity_type='password_reset_complete',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': 'Password reset successfully'
        })


class EmailVerificationView(generics.GenericAPIView):
    """Email verification endpoint"""
    
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Invalid verification link'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({
                'error': 'Invalid or expired verification link'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_verified:
            return Response({
                'message': 'Email already verified'
            })
        
        user.is_verified = True
        user.save()
        
        # Log email verification
        log_user_activity(
            user=user,
            activity_type='email_verification',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': 'Email verified successfully'
        })


class ResendVerificationView(generics.GenericAPIView):
    """Resend verification email endpoint"""
    
    serializer_class = ResendVerificationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email, is_active=True)
        
        send_verification_email(user, request)
        
        return Response({
            'message': 'Verification email sent successfully'
        })


class UserActivityViewSet(ReadOnlyModelViewSet):
    """User activity viewset"""
    
    serializer_class = UserActivitySerializer
    permission_classes = [IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['activity_type']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        # Handle schema generation (swagger fake view)
        if getattr(self, 'swagger_fake_view', False):
            return UserActivity.objects.none()
        
        # Handle anonymous users
        if not self.request.user.is_authenticated:
            return UserActivity.objects.none()
        
        if self.request.user.is_staff:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=self.request.user)


class UserSessionViewSet(ReadOnlyModelViewSet):
    """User session viewset"""
    
    serializer_class = UserSessionSerializer
    permission_classes = [IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['created_at', 'last_activity']
    ordering = ['-last_activity']
    
    def get_queryset(self):
        # Handle schema generation (swagger fake view)
        if getattr(self, 'swagger_fake_view', False):
            return UserSession.objects.none()
        
        # Handle anonymous users
        if not self.request.user.is_authenticated:
            return UserSession.objects.none()
        
        if self.request.user.is_staff:
            return UserSession.objects.all()
        return UserSession.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a session"""
        session = self.get_object()
        
        # Check permission
        if not request.user.is_staff and session.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session.terminate()
        
        return Response({
            'message': 'Session terminated successfully'
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'user-service',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def service_info(request):
    """Service information endpoint"""
    return Response({
        'name': settings.SERVICE_NAME,
        'version': settings.SERVICE_VERSION,
        'description': 'User management microservice',
        'endpoints': {
            'auth': '/api/auth/',
            'users': '/api/users/',
            'profiles': '/api/profiles/',
            'activities': '/api/activities/',
            'sessions': '/api/sessions/',
            'health': '/api/health/',
            'docs': '/api/docs/'
        }
    })