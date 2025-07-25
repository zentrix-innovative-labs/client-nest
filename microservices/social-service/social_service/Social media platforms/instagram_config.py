from django.conf import settings
import os

# Instagram Basic Display API Configuration
INSTAGRAM_CONFIG = {
    'CLIENT_ID': os.getenv('INSTAGRAM_CLIENT_ID', ''),
    'CLIENT_SECRET': os.getenv('INSTAGRAM_CLIENT_SECRET', ''),
    'REDIRECT_URI': os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:8000/api/social/instagram/callback/'),
    'SCOPE': [
        'user_profile',
        'user_media'
    ],
    'USE_PROXY': os.getenv('USE_PROXY', 'False').lower() == 'true',  # Default to False for security
    'PROXY_URL': 'https://api.allorigins.win/raw?url=',  # Example proxy service
}  # Note: Using a proxy can pose security risks. Ensure the proxy service is trusted and suitable for your use case.

# Instagram API Endpoints
INSTAGRAM_ENDPOINTS = {
    'AUTH_URL': 'https://api.instagram.com/oauth/authorize',
    'TOKEN_URL': 'https://api.instagram.com/oauth/access_token',
    'GRAPH_URL': 'https://graph.instagram.com/me',
    'MEDIA_URL': 'https://graph.instagram.com/me/media'
} 
