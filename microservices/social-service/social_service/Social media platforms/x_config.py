"""
X (Twitter) API Configuration

Note: Access tokens are stored per-user in the database (SocialAccount model),
not in environment variables. Only API_KEY and API_SECRET are needed for OAuth flow.
"""

import os
from dotenv import load_dotenv

# Load the .env file dynamically based on ENV_PATH environment variable or default to '../.env'
env_path = os.getenv('ENV_PATH', os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(env_path)

X_CONFIG = {
    'API_KEY': os.getenv('X_API_KEY'),
    'API_SECRET': os.getenv('X_API_SECRET'),
    'BEARER_TOKEN': os.getenv('X_BEARER_TOKEN'),
    'REDIRECT_URI': os.getenv('X_REDIRECT_URI', 'http://localhost:8000/api/social/x/callback/'),
}

X_ENDPOINTS = {
    'REQUEST_TOKEN_URL': 'https://api.twitter.com/oauth/request_token',
    'AUTH_URL': 'https://api.twitter.com/oauth/authorize',
    'ACCESS_TOKEN_URL': 'https://api.twitter.com/oauth/access_token',
    'API_URL': 'https://api.twitter.com/2',
    'UPLOAD_URL': 'https://upload.twitter.com/1.1/media/upload.json',
}

X_SCOPES = [
    'tweet.read',
    'tweet.write',
    'user_service.read',
    'offline.access',
] 
