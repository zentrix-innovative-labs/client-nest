import requests
from .x_config import X_CONFIG, X_ENDPOINTS
try:
    from .models import SocialAccount
except ImportError:
    from social_service.models import SocialAccount
from django.conf import settings
import json
import base64
from datetime import datetime
from requests_oauthlib import OAuth1Session
import logging
import os

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
        """Upload media to X using streaming chunked upload for improved memory efficiency."""
        BYTES_PER_MB = 1024 * 1024
        ENV_MAX_MB = 100
        max_file_size = int(os.getenv('X_MAX_FILE_SIZE', 10 * BYTES_PER_MB))  # 10 MB default
        hard_max_file_size = ENV_MAX_MB * BYTES_PER_MB
        if max_file_size > hard_max_file_size:
            max_file_size = hard_max_file_size
        file_size = os.path.getsize(media_file.name)
        if file_size > max_file_size:
            raise ValueError(f"File size exceeds the maximum limit of {max_file_size} bytes.")

        # Re-check file size immediately before reading/uploading
        media_file.seek(0, 2)
        current_size = media_file.tell()
        media_file.seek(0)
        if current_size != file_size:
            raise ValueError("File size changed after initial validation. This may indicate tampering, corruption, or unexpected modifications to the file. Aborting upload for security.")
        
        upload_url = X_ENDPOINTS['UPLOAD_URL']
        
        # 1. INIT
        init_data = {
            'command': 'INIT',
            'media_type': media_type,
            'total_bytes': file_size
        }
        init_resp = self.oauth.post(upload_url, data=init_data)
        init_resp.raise_for_status()
        media_id = init_resp.json()['media_id_string']
        
        # 2. APPEND (chunked upload)
        chunk_size = 4 * BYTES_PER_MB  # 4 MB per Twitter docs
        segment_index = 0
        media_file.seek(0)
        while True:
            chunk = media_file.read(chunk_size)
            if not chunk:
                break
            append_data = {
                'command': 'APPEND',
                'media_id': media_id,
                'segment_index': segment_index
            }
            files = {
                'media': chunk
            }
            append_resp = self.oauth.post(upload_url, data=append_data, files=files)
            append_resp.raise_for_status()
            segment_index += 1
        
        # 3. FINALIZE
        finalize_data = {
            'command': 'FINALIZE',
            'media_id': media_id
        }
        finalize_resp = self.oauth.post(upload_url, data=finalize_data)
        finalize_resp.raise_for_status()
        return finalize_resp.json()

    def get_analytics(self, tweet_id):
        """Get analytics for a specific tweet (Twitter API v2)"""
        params = {'tweet.fields': 'public_metrics,non_public_metrics,organic_metrics'}
        return self._make_request('GET', f'tweets/{tweet_id}', params=params)

    def get_timeline(self, user_id=None, max_results=10):
        """Get user's timeline"""
        params = {'max_results': max_results}
        if user_id:
            params['user_id'] = user_id
        return self._make_request('GET', 'tweets', params=params)

    def delete_post(self, tweet_id):
        """Delete a tweet"""
        return self._make_request('DELETE', f'tweets/{tweet_id}')

    def get_mentions(self, user_id, max_results=10):
        """Get mentions of the specified user (Twitter API v2)"""
        if not user_id:
            raise ValueError("user_id is required to fetch mentions.")
        params = {'max_results': max_results}
        return self._make_request('GET', f'users/{user_id}/mentions', params=params)

    def get_followers(self, user_id, max_results=10):
        """Get user's followers"""
        if not user_id:
            raise ValueError("user_id is required to fetch followers.")
        params = {'max_results': max_results}
        return self._make_request('GET', f'users/{user_id}/followers', params=params)

    def get_following(self, user_id, max_results=10):
        """Get users that the specified user follows"""
        if not user_id:
            raise ValueError("user_id is required for the 'get_following' method.")
        params = {'max_results': max_results}
        return self._make_request('GET', f'users/{user_id}/following', params=params) 
