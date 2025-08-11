#!/usr/bin/env python3
"""
Test script to verify User Service endpoints are accessible
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    """Test basic endpoints"""
    
    print("🔍 Testing User Service Endpoints\n")
    
    # Test service info
    print("1. Testing Service Info...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✅ Service Info OK")
            data = response.json()
            print(f"   📋 Service: {data.get('name')}")
            print(f"   📋 Version: {data.get('version')}")
        else:
            print(f"   ❌ Service Info Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Service Info Error: {e}")
    
    # Test health check
    print("\n2. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code == 200:
            print("   ✅ Health Check OK")
            data = response.json()
            print(f"   📋 Status: {data.get('status')}")
        else:
            print(f"   ❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health Check Error: {e}")
    
    # Test Swagger JSON
    print("\n3. Testing Swagger API Schema...")
    try:
        response = requests.get(f"{BASE_URL}/swagger.json")
        if response.status_code == 200:
            print("   ✅ Swagger Schema OK")
            data = response.json()
            print(f"   📋 API Title: {data.get('info', {}).get('title')}")
            print(f"   📋 Endpoints Found: {len(data.get('paths', {}))}")
        else:
            print(f"   ❌ Swagger Schema Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Swagger Schema Error: {e}")
    
    # Test Swagger UI accessibility
    print("\n4. Testing Swagger UI...")
    try:
        response = requests.get(f"{BASE_URL}/swagger/")
        if response.status_code == 200:
            print("   ✅ Swagger UI OK")
            print(f"   📋 Content Length: {len(response.content)} bytes")
            if "swagger-ui" in response.text.lower():
                print("   📋 Swagger UI content detected")
            else:
                print("   ⚠️  Swagger UI content not clearly detected")
        else:
            print(f"   ❌ Swagger UI Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Swagger UI Error: {e}")
    
    print("\n" + "="*50)
    print("📊 Test Summary:")
    print(f"🌐 Access Swagger UI at: {BASE_URL}/swagger/")
    print(f"📖 Access ReDoc at: {BASE_URL}/redoc/")
    print(f"🔧 API Schema JSON: {BASE_URL}/swagger.json")
    print("="*50)

def test_registration_endpoint():
    """Test if registration endpoint is accessible"""
    print("\n5. Testing Registration Endpoint Structure...")
    try:
        # We don't actually register, just test if the endpoint exists
        response = requests.post(f"{BASE_URL}/api/v1/users/auth/register/", 
                               json={}, headers={'Content-Type': 'application/json'})
        
        if response.status_code in [400, 422]:  # Bad request is expected with empty data
            print("   ✅ Registration Endpoint Accessible")
            print("   📋 Endpoint properly configured (returns validation errors as expected)")
        elif response.status_code == 404:
            print("   ❌ Registration Endpoint Not Found")
        else:
            print(f"   ⚠️  Registration Endpoint Unexpected Response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Registration Endpoint Error: {e}")

if __name__ == "__main__":
    test_endpoints()
    test_registration_endpoint()
    
    print("\n💡 Tips:")
    print("   • Open http://127.0.0.1:8000/swagger/ in your browser")
    print("   • Click 'Authorize' button to add JWT token")
    print("   • Use /auth/login/ endpoint to get a token first")
    print("   • Copy the access_token and paste in format: Bearer <token>")
