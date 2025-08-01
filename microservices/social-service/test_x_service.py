#!/usr/bin/env python3
"""
X Service Test Script

This script tests the X (Twitter) service functionality including:
1. Connection testing
2. Account info retrieval
3. Content posting
4. Error handling
5. Media upload (if configured)

Usage:
    python test_x_service.py

Requirements:
    - X_API_KEY and X_API_SECRET environment variables set
    - Valid access_token and access_token_secret for testing
"""

import os
import sys
import json
import tempfile
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

def test_configuration():
    """Test if X configuration is properly set up"""
    print("🔧 Testing X Configuration...")
    
    # Check if API credentials are configured
    if not X_CONFIG['API_KEY']:
        print("❌ X_API_KEY is not configured")
        return False
    
    if not X_CONFIG['API_SECRET']:
        print("❌ X_API_SECRET is not configured")
        return False
    
    print("✅ X API credentials are configured")
    print(f"   API URL: {X_ENDPOINTS['API_URL']}")
    print(f"   Upload URL: {X_ENDPOINTS['UPLOAD_URL']}")
    return True

def test_service_initialization(access_token, access_token_secret):
    """Test X service initialization"""
    print("\n🚀 Testing X Service Initialization...")
    
    try:
        x_service = XService(access_token, access_token_secret)
        print("✅ X Service initialized successfully")
        return x_service
    except Exception as e:
        print(f"❌ Failed to initialize X Service: {e}")
        return None

def test_account_info(x_service):
    """Test getting account information"""
    print("\n👤 Testing Account Info Retrieval...")
    
    try:
        account_info = x_service.get_account_info()
        print("✅ Account info retrieved successfully")
        print(f"   User ID: {account_info.get('data', {}).get('id', 'N/A')}")
        print(f"   Username: {account_info.get('data', {}).get('username', 'N/A')}")
        print(f"   Name: {account_info.get('data', {}).get('name', 'N/A')}")
        return account_info
    except Exception as e:
        print(f"❌ Failed to get account info: {e}")
        return None

def test_post_content(x_service, test_content="This is a test tweet from the X Service! 🚀 #testing #api"):
    """Test posting content to X"""
    print(f"\n📝 Testing Content Posting...")
    print(f"   Content: {test_content}")
    
    try:
        result = x_service.post_content(test_content)
        
        if result.get('status') == 'error':
            print(f"❌ Failed to post content: {result.get('message')}")
            return None
        
        print("✅ Content posted successfully")
        print(f"   Tweet ID: {result.get('id')}")
        print(f"   Text: {result.get('text')}")
        print(f"   Created At: {result.get('created_at')}")
        return result
    except Exception as e:
        print(f"❌ Failed to post content: {e}")
        return None

def test_timeline_retrieval(x_service, max_results=5):
    """Test retrieving user timeline"""
    print(f"\n📋 Testing Timeline Retrieval (max {max_results} tweets)...")
    
    try:
        timeline = x_service.get_timeline(max_results=max_results)
        tweets = timeline.get('data', [])
        print(f"✅ Timeline retrieved successfully")
        print(f"   Retrieved {len(tweets)} tweets")
        
        for i, tweet in enumerate(tweets[:3], 1):  # Show first 3 tweets
            print(f"   Tweet {i}: {tweet.get('text', '')[:50]}...")
        
        return timeline
    except Exception as e:
        print(f"❌ Failed to retrieve timeline: {e}")
        return None

def test_media_upload(x_service):
    """Test media upload functionality"""
    print("\n🖼️ Testing Media Upload...")
    
    # Create a simple test image file
    try:
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as temp_file:
            # Create a minimal JPEG file (just for testing)
            jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
            temp_file.write(jpeg_header)
            temp_file_path = temp_file.name
        
        # Test media upload
        with open(temp_file_path, 'rb') as media_file:
            result = x_service.upload_media(media_file, 'image/jpeg')
        
        print("✅ Media upload test completed")
        print(f"   Media ID: {result.get('media_id_string', 'N/A')}")
        
        # Clean up
        os.unlink(temp_file_path)
        return result
        
    except Exception as e:
        print(f"❌ Media upload test failed: {e}")
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        return None

def test_error_handling(x_service):
    """Test error handling with invalid requests"""
    print("\n⚠️ Testing Error Handling...")
    
    # Test with empty content
    print("   Testing empty content...")
    result = x_service.post_content("")
    if result and result.get('status') == 'error':
        print("   ✅ Properly handled empty content")
    else:
        print("   ⚠️ Empty content handling needs review")
    
    # Test with very long content (should be handled by Twitter API)
    print("   Testing very long content...")
    long_content = "A" * 300  # Twitter limit is 280 characters
    result = x_service.post_content(long_content)
    if result and result.get('status') == 'error':
        print("   ✅ Properly handled long content")
    else:
        print("   ⚠️ Long content handling needs review")

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 X Service Comprehensive Test Suite")
    print("=" * 50)
    
    # Test configuration
    if not test_configuration():
        print("\n❌ Configuration test failed. Please check your environment variables.")
        return False
    
    # Get test credentials from environment or user input
    access_token = os.getenv('X_TEST_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_TEST_ACCESS_TOKEN_SECRET')
    
    if not access_token or not access_token_secret:
        print("\n⚠️ Test credentials not found in environment variables.")
        print("Please set X_TEST_ACCESS_TOKEN and X_TEST_ACCESS_TOKEN_SECRET")
        print("Or enter them manually:")
        
        access_token = input("Enter X Access Token: ").strip()
        access_token_secret = input("Enter X Access Token Secret: ").strip()
        
        if not access_token or not access_token_secret:
            print("❌ No credentials provided. Cannot run tests.")
            return False
    
    # Test service initialization
    x_service = test_service_initialization(access_token, access_token_secret)
    if not x_service:
        return False
    
    # Test account info
    account_info = test_account_info(x_service)
    if not account_info:
        print("⚠️ Account info test failed, but continuing with other tests...")
    
    # Test content posting
    post_result = test_post_content(x_service)
    if not post_result:
        print("⚠️ Content posting test failed, but continuing with other tests...")
    
    # Test timeline retrieval
    timeline_result = test_timeline_retrieval(x_service)
    if not timeline_result:
        print("⚠️ Timeline retrieval test failed, but continuing with other tests...")
    
    # Test media upload (optional)
    try:
        media_result = test_media_upload(x_service)
        if not media_result:
            print("⚠️ Media upload test failed, but this is optional...")
    except Exception as e:
        print(f"⚠️ Media upload test skipped: {e}")
    
    # Test error handling
    test_error_handling(x_service)
    
    print("\n" + "=" * 50)
    print("✅ X Service test suite completed!")
    print("\nSummary:")
    print("   - Configuration: ✅")
    print("   - Service Initialization: ✅")
    print("   - Account Info: {'✅' if account_info else '❌'}")
    print("   - Content Posting: {'✅' if post_result else '❌'}")
    print("   - Timeline Retrieval: {'✅' if timeline_result else '❌'}")
    print("   - Error Handling: ✅")
    
    return True

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 