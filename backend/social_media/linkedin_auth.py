import os
print("LINKEDIN_CLIENT_ID:", os.environ.get("LINKEDIN_CLIENT_ID"))
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import redirect
from .models import SocialAccount
import requests
import urllib.parse
from .linkedin_config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI
from rest_framework.permissions import AllowAny
import uuid

class LinkedInAuthView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        state = str(uuid.uuid4())
        request.session['linkedin_state'] = state
        params = {
            'response_type': 'code',
            'client_id': LINKEDIN_CLIENT_ID,
            'redirect_uri': LINKEDIN_REDIRECT_URI,
            'scope': 'r_liteprofile w_member_social',
            'state': state  # Unique per request
        }
        url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
        return redirect(url)

class LinkedInCallbackView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        session_state = request.session.get('linkedin_state')
        if not code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not state or not session_state or state != session_state:
            return Response({'error': 'Invalid or missing state parameter'}, status=status.HTTP_400_BAD_REQUEST)
        # Optionally, remove the state from session after validation
        del request.session['linkedin_state']
        token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': LINKEDIN_REDIRECT_URI,
            'client_id': LINKEDIN_CLIENT_ID,
            'client_secret': LINKEDIN_CLIENT_SECRET
        }
        response = requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            # Fetch LinkedIn user ID using the access token
            profile_url = 'https://api.linkedin.com/v2/me'
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.get(profile_url, headers=headers)
            if profile_response.status_code != 200:
                return Response({'error': 'Failed to fetch LinkedIn user profile', 'details': profile_response.json()}, status=profile_response.status_code)
            profile_data = profile_response.json()
            linkedin_id = profile_data.get('id')
            if not linkedin_id:
                return Response({'error': 'LinkedIn user ID not found in profile data', 'details': profile_data}, status=400)
            # Save the access token and LinkedIn user ID to the user's SocialAccount
            if not request.user or not request.user.is_authenticated:
                return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            social_account, created = SocialAccount.objects.get_or_create(
                user=request.user,
                platform='linkedin',
                account_id=linkedin_id
            )
            social_account.access_token = access_token
            # Optionally handle expires_in and token_expires_at
            social_account.save()
            return Response({'status': 'success', 'token_data': token_data, 'linkedin_id': linkedin_id})
        else:
            return Response({'error': 'Failed to obtain access token', 'details': response.json()}, status=response.status_code) 