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

class LinkedInAuthView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        params = {
            'response_type': 'code',
            'client_id': LINKEDIN_CLIENT_ID,
            'redirect_uri': LINKEDIN_REDIRECT_URI,
            'scope': 'r_liteprofile w_member_social',
            'state': 'random_state_string'  # In production, generate and validate this
        }
        url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
        return redirect(url)

class LinkedInCallbackView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        if not code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)
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
            # Here, you would save the access token to the user's SocialAccount
            return Response({'status': 'success', 'token_data': token_data})
        else:
            return Response({'error': 'Failed to obtain access token', 'details': response.json()}, status=response.status_code) 