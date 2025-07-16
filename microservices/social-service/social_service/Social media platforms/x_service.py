import requests
from .x_config import X_CONFIG, X_ENDPOINTS
from .models import SocialAccount
from django.conf import settings
import json
import base64
from datetime import datetime
from requests_oauthlib import OAuth1Session
import logging

logger = logging.getLogger(__name__)

SENSITIVE_HEADERS = frozenset({'authorization', 'cookie', 'set-cookie'})

def redact_headers(headers):
    return {k: ('<REDACTED>' if k.lower() in SENSITIVE_HEADERS else v) for k, v in headers.items()}

class XService:
    def __init__(self, access_token, access_token_secret):
        # Removed commented-out print statements for sensitive debug output
        logger.debug("[DEBUG] XService.__init__ values:")
        logger.debug("  API_KEY: %s", "<REDACTED>")
        logger.debug("  API_SECRET: %s", "<REDACTED>")
        logger.debug("  access_token: %s", access_token[:4] + "..." if access_token else "<REDACTED>")
        logger.debug("  access_token_secret: %s", access_token_secret[:4] + "..." if access_token_secret else "<REDACTED>")
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.oauth = OAuth1Session(
            client_key=X_CONFIG['API_KEY'],
            client_secret=X_CONFIG['API_SECRET'],
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
            signature_type='auth_header'
        )

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make a request to the X API"""
        url = f"{X_ENDPOINTS['API_URL']}/{endpoint}"
        response = self.oauth.request(
            method,
            url,
            json=data,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_account_info(self):
        """Get X account information"""
        response = self.oauth.get(f"{X_ENDPOINTS['API_URL']}/users/me")
        return response.json()

    def post_content(self, content):
        """Post content to X"""
        try:
            data = {
                'text': content
            }
            response = self.oauth.post(f"{X_ENDPOINTS['API_URL']}/tweets", json=data)
            logger.info("Response status code: %s", response.status_code)
            logger.debug("Response headers: %s", redact_headers(response.headers))
            # Truncate response content to avoid logging sensitive or PII data (Copilot suggestion)
            logger.debug("Response content (truncated): %s", response.text[:200] + ('...' if len(response.text) > 200 else ''))
            
            if response.status_code != 201:  # Twitter API v2 returns 201 for successful creation
                return {
                    'status': 'error',
                    'message': f'X API returned status code {response.status_code}: {response.text}'
                }
            
            try:
                response_data = response.json()
                tweet_data = response_data.get('data', {})
                return {
                    'id': tweet_data.get('id'),
                    'text': tweet_data.get('text'),
                    'created_at': tweet_data.get('created_at')
                }
            except ValueError as e:
                logger.exception("JSON parsing error")
                return {
                    'status': 'error',
                    'message': f'Invalid JSON response from X API: {response.text}'
                }
        except Exception as e:
            logger.exception("Exception in post_content")
            return {
                'status': 'error',
                'message': str(e)
            }

    def upload_media(self, media_file, media_type):
        """Upload media to X with file size validation and streaming base64 encoding"""
        import os
        from base64 import b64encode
        
        # Validate file size (10 MB limit)
        max_file_size = 10 * 1024 * 1024  # 10 MB
        file_size = os.path.getsize(media_file.name)
        if file_size > max_file_size:
            raise ValueError(f"File size exceeds the maximum limit of {max_file_size} bytes.")
        
        # Stream base64 encoding
        def encode_file(file):
            file.seek(0)
            for chunk in iter(lambda: file.read(8192), b""):
                yield b64encode(chunk).decode('utf-8')
        
        upload_url = X_ENDPOINTS['UPLOAD_URL']
        media_data = {
            'media_type': media_type,
            'media': ''.join(encode_file(media_file))
        }
        response = self.oauth.post(
            upload_url,
            data=media_data
        )
        response.raise_for_status()
        return response.json()

    def get_analytics(self, tweet_id):
        """Get analytics for a specific tweet"""
        return self._make_request('GET', f'tweets/{tweet_id}/metrics')

    def get_timeline(self, user_id=None, max_results=10):
        """Get user's timeline"""
        params = {'max_results': max_results}
        if user_id:
            params['user_id'] = user_id
        return self._make_request('GET', 'tweets', params=params)

    def delete_post(self, tweet_id):
        """Delete a tweet"""
        return self._make_request('DELETE', f'tweets/{tweet_id}')

    def get_mentions(self, max_results=10):
        """Get mentions of the authenticated user"""
        params = {'max_results': max_results}
        return self._make_request('GET', 'tweets/mentions', params=params)

    def get_followers(self, user_id=None, max_results=10):
        """Get user's followers"""
        params = {'max_results': max_results}
        if user_id:
            params['user_id'] = user_id
        return self._make_request('GET', 'users/followers', params=params)

    def get_following(self, user_id=None, max_results=10):
        """Get users that the authenticated user follows"""
        params = {'max_results': max_results}
        if user_id:
            params['user_id'] = user_id
        return self._make_request('GET', 'users/following', params=params) 
