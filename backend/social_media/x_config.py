"""
X (Twitter) API Configuration
"""

X_CONFIG = {
    'API_KEY': 'mlNmcNVg5nBNrnY1bEaHqLupk',
    'API_SECRET': 'o9X9C2u6U6m5RzzZyLGC89wL0xWTnmUNGjA6ifbx5WQgw8Z6nU',
    'ACCESS_TOKEN': '1689656332859711491-OBhoS7RV4u3L5taiMP8zovImM2uuel',
    'ACCESS_TOKEN_SECRET': 'rCzWk0TTLmXOOlD5a5ONI8jWiO8fojC8CV23kWoxbqsge',
    'REDIRECT_URI': 'http://localhost:8000/api/social/x/callback/',
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
    'users.read',
    'offline.access',
] 