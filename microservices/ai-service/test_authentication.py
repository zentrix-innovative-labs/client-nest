#!/usr/bin/env python3
"""
Test script to verify authentication is working correctly
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
django.setup()

User = get_user_model()

def test_authentication_flow():
    """Test that authentication is working correctly"""
    print("🔐 Testing Authentication Flow")
    print("=" * 40)
    
    # Create a test user
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Test 1: Unauthenticated request should fail
    print("\n1. Testing unauthenticated request...")
    client = APIClient()
    response = client.post('/api/ai/generate/content/', {
        'topic': 'AI in business',
        'platform': 'linkedin',
        'tone': 'professional'
    })
    
    if response.status_code == 401:
        print("✅ Unauthenticated request properly rejected (401)")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Expected 401, got {response.status_code}")
    
    # Test 2: Authenticated request should work
    print("\n2. Testing authenticated request...")
    client.force_authenticate(user=user)
    
    # We'll mock the response since we don't have AI service running
    from unittest.mock import patch
    from content_generation.logic import ContentGenerator
    
    mock_response = {
        'content': 'Test generated content about AI in business',
        'hashtags': ['#AI', '#Business', '#Innovation'],
        'quality_score': 85,
        'safety_check': {'is_safe': True, 'reason': 'Content is safe'},
        'readability_score': 75.5,
        'call_to_action': 'Learn more about AI implementation',
        'suggestions': ['Add more specific examples'],
        'variations': [{'version': 1, 'content': 'Alternative content'}],
        'engagement_prediction': 'high',
        'optimal_posting_time_suggestion': '9:00 AM - 11:00 AM on weekdays'
    }
    
    with patch.object(ContentGenerator, 'generate_post', return_value=mock_response):
        response = client.post('/api/ai/generate/content/', {
            'topic': 'AI in business',
            'platform': 'linkedin',
            'tone': 'professional'
        })
        
        if response.status_code == 200:
            print("✅ Authenticated request successful (200)")
            print(f"   Generated content: {response.json()['content'][:50]}...")
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            print(f"   Response: {response.json()}")
    
    # Test 3: Health check should always work
    print("\n3. Testing health check (should always work)...")
    unauthenticated_client = APIClient()
    response = unauthenticated_client.get('/health/')
    
    if response.status_code == 200:
        print("✅ Health check works without authentication (200)")
        print(f"   Status: {response.json()['status']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    
    # Test 4: Test other secured endpoints
    print("\n4. Testing other secured endpoints...")
    
    secured_endpoints = [
        ('/api/ai/analyze/sentiment/', {'text': 'This is a test message'}),
        ('/api/ai/usage/stats/', None),
        ('/api/ai/token/usage/', None),
    ]
    
    for endpoint, payload in secured_endpoints:
        # Test without authentication
        unauthenticated_client = APIClient()
        if payload:
            response = unauthenticated_client.post(endpoint, payload)
        else:
            response = unauthenticated_client.get(endpoint)
        
        if response.status_code == 401:
            print(f"✅ {endpoint} properly secured (401 without auth)")
        else:
            print(f"❌ {endpoint} not properly secured ({response.status_code})")
    
    print("\n🎉 Authentication test completed!")
    print("=" * 40)

if __name__ == '__main__':
    test_authentication_flow()
