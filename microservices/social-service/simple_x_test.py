#!/usr/bin/env python3
"""
Simple X Service Test

Quick test to verify X service is working properly.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_service.settings')

import django
django.setup()

from social_service.Social_media_platforms.x_service import XService
from social_service.Social_media_platforms.x_config import X_CONFIG, X_ENDPOINTS

def test_x_service():
    """Test X service basic functionality"""
    print("🧪 Testing X Service...")
    
    # Check configuration
    print("1. Checking configuration...")
    if not X_CONFIG['API_KEY']:
        print("❌ X_API_KEY not found")
        return False
    if not X_CONFIG['API_SECRET']:
        print("❌ X_API_SECRET not found")
        return False
    print("✅ Configuration OK")
    
    # Get test credentials
    access_token = os.getenv('X_TEST_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_TEST_ACCESS_TOKEN_SECRET')
    
    if not access_token or not access_token_secret:
        print("❌ Test credentials not found. Set X_TEST_ACCESS_TOKEN and X_TEST_ACCESS_TOKEN_SECRET")
        return False
    
    # Test service initialization
    print("2. Testing service initialization...")
    try:
        x_service = XService(access_token, access_token_secret)
        print("✅ Service initialized")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False
    
    # Test account info
    print("3. Testing account info...")
    try:
        account_info = x_service.get_account_info()
        print("✅ Account info retrieved")
        user_data = account_info.get('data', {})
        print(f"   User: @{user_data.get('username', 'N/A')} ({user_data.get('name', 'N/A')})")
    except Exception as e:
        print(f"❌ Account info failed: {e}")
        return False
    
    # Test posting (optional)
    print("4. Testing content posting...")
    test_content = "Test tweet from X Service! 🚀 #testing"
    try:
        result = x_service.post_content(test_content)
        if result.get('status') == 'error':
            print(f"❌ Posting failed: {result.get('message')}")
        else:
            print("✅ Content posted successfully")
            print(f"   Tweet ID: {result.get('id')}")
    except Exception as e:
        print(f"❌ Posting failed: {e}")
    
    print("\n✅ X Service test completed!")
    return True

if __name__ == "__main__":
    test_x_service() 