from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import authenticate
from django.conf import settings
import requests
import logging
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_token(request):
    """
    Validate JWT token for incoming requests
    This endpoint is used by the gateway middleware to validate tokens
    """
    token = request.data.get('token')
    if not token:
        return Response({
            'valid': False,
            'error': 'Token not provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Try to decode the token
        access_token = AccessToken(token)
        
        # Get user information from token
        user_id = access_token.get('user_id')
        
        # Optionally, you can make a request to user service to get full user data
        # For now, we'll just return the user_id from the token
        
        return Response({
            'valid': True,
            'user_id': user_id,
            'token_type': 'access',
            'expires_at': datetime.fromtimestamp(access_token.get('exp')).isoformat()
        })
        
    except TokenError as e:
        return Response({
            'valid': False,
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return Response({
            'valid': False,
            'error': 'Invalid token format'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def proxy_login(request):
    """
    Proxy login request to user service
    This allows the gateway to handle authentication centrally
    """
    try:
        # Get user service URL from settings
        user_service_url = settings.MICROSERVICES.get('USER_SERVICE', {}).get('BASE_URL')
        if not user_service_url:
            return Response({
                'error': 'User service not configured'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Forward the login request to user service
        login_url = f"{user_service_url.rstrip('/')}/api/auth/login/"
        
        response = requests.post(
            login_url,
            json=request.data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Return the response from user service
        return Response(
            response.json() if response.content else {},
            status=response.status_code
        )
        
    except requests.RequestException as e:
        logger.error(f"Login proxy error: {str(e)}")
        return Response({
            'error': 'Authentication service unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(f"Unexpected login error: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def proxy_register(request):
    """
    Proxy registration request to user service
    """
    try:
        # Get user service URL from settings
        user_service_url = settings.MICROSERVICES.get('USER_SERVICE', {}).get('BASE_URL')
        if not user_service_url:
            return Response({
                'error': 'User service not configured'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Forward the registration request to user service
        register_url = f"{user_service_url.rstrip('/')}/api/auth/register/"
        
        response = requests.post(
            register_url,
            json=request.data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Return the response from user service
        return Response(
            response.json() if response.content else {},
            status=response.status_code
        )
        
    except requests.RequestException as e:
        logger.error(f"Registration proxy error: {str(e)}")
        return Response({
            'error': 'Registration service unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(f"Unexpected registration error: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def proxy_refresh_token(request):
    """
    Proxy token refresh request to user service
    """
    try:
        # Get user service URL from settings
        user_service_url = settings.MICROSERVICES.get('USER_SERVICE', {}).get('BASE_URL')
        if not user_service_url:
            return Response({
                'error': 'User service not configured'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Forward the refresh request to user service
        refresh_url = f"{user_service_url.rstrip('/')}/api/auth/refresh/"
        
        response = requests.post(
            refresh_url,
            json=request.data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Return the response from user service
        return Response(
            response.json() if response.content else {},
            status=response.status_code
        )
        
    except requests.RequestException as e:
        logger.error(f"Token refresh proxy error: {str(e)}")
        return Response({
            'error': 'Token refresh service unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(f"Unexpected token refresh error: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """
    Get user information from token
    This endpoint extracts user info from the validated JWT token
    """
    try:
        # Get the token from the request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({
                'error': 'Invalid authorization header'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        access_token = AccessToken(token)
        
        # Extract user information from token
        user_info = {
            'user_id': access_token.get('user_id'),
            'username': access_token.get('username'),
            'email': access_token.get('email'),
            'is_staff': access_token.get('is_staff', False),
            'is_superuser': access_token.get('is_superuser', False),
            'token_type': access_token.get('token_type'),
            'expires_at': datetime.fromtimestamp(access_token.get('exp')).isoformat()
        }
        
        return Response(user_info)
        
    except TokenError as e:
        return Response({
            'error': 'Invalid or expired token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user by blacklisting the refresh token
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Successfully logged out'
        })
        
    except TokenError:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for the auth service
    """
    return Response({
        'status': 'healthy',
        'service': 'auth-service',
        'timestamp': datetime.now().isoformat()
    })
