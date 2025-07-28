#!/usr/bin/env python3
"""
X API Test Script

Test X service endpoints via HTTP requests.
"""

import requests
import json
import os
import sys

def test_x_connection_endpoint(base_url="http://localhost:8000", token=None):
    """Test X connection endpoint"""
    print("🔗 Testing X Connection Endpoint...")
    
    url = f"{base_url}/api/social/x/test-connection/"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Connection successful")
            print(f"   Account Info: {data.get('account_info', {}).get('data', {}).get('username', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("   ❌ Authentication required")
            return False
        elif response.status_code == 404:
            print("   ❌ No active X account found")
            return False
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_x_post_endpoint(base_url="http://localhost:8000", token=None, content="Test tweet from API! 🚀"):
    """Test X post endpoint"""
    print(f"\n📝 Testing X Post Endpoint...")
    print(f"   Content: {content}")
    
    url = f"{base_url}/api/social/x/test-post/"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    data = {'content': content}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Post successful")
            print(f"   Tweet ID: {data.get('tweet_id', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("   ❌ Authentication required")
            return False
        elif response.status_code == 400:
            print(f"   ❌ Bad request: {response.text}")
            return False
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_social_accounts_status(base_url="http://localhost:8000", token=None):
    """Test social accounts status endpoint"""
    print("\n📊 Testing Social Accounts Status...")
    
    url = f"{base_url}/api/social/accounts/status/"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Status retrieved")
            
            x_status = data.get('x_account', {}).get('status', 'unknown')
            linkedin_status = data.get('linkedin_account', {}).get('status', 'unknown')
            
            print(f"   X Account: {x_status}")
            print(f"   LinkedIn Account: {linkedin_status}")
            return True
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 X API Test Suite")
    print("=" * 50)
    
    # Get configuration
    base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    token = os.getenv('API_TOKEN')
    
    print(f"Base URL: {base_url}")
    print(f"Token: {'Set' if token else 'Not set'}")
    
    # Test endpoints
    connection_ok = test_x_connection_endpoint(base_url, token)
    post_ok = test_x_post_endpoint(base_url, token)
    status_ok = test_social_accounts_status(base_url, token)
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"   Connection Test: {'✅' if connection_ok else '❌'}")
    print(f"   Post Test: {'✅' if post_ok else '❌'}")
    print(f"   Status Test: {'✅' if status_ok else '❌'}")
    
    if not token:
        print("\n💡 Tip: Set API_TOKEN environment variable for authenticated tests")
    
    return all([connection_ok, post_ok, status_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 