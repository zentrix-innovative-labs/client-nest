#!/usr/bin/env python3
"""
Standalone X Service Test

Test X service configuration without Django setup.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_x_config():
    """Test X configuration loading"""
    print("🔧 Testing X Configuration...")
    
    # Check environment variables
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    
    if not api_key:
        print("❌ X_API_KEY not found")
        return False
    
    if not api_secret:
        print("❌ X_API_SECRET not found")
        return False
    
    print("✅ Environment variables loaded")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   API Secret: {api_secret[:10]}...")
    
    # Test importing the config module
    try:
        # Add the social_service directory to path
        social_service_dir = current_dir / 'social_service'
        sys.path.insert(0, str(social_service_dir))
        
        # Try to import the config
        from Social_media_platforms.x_config import X_CONFIG, X_ENDPOINTS
        
        print("✅ Configuration module imported successfully")
        print(f"   API URL: {X_ENDPOINTS['API_URL']}")
        print(f"   Upload URL: {X_ENDPOINTS['UPLOINT_URL']}")
        
        # Check if config loaded the environment variables
        if X_CONFIG['API_KEY'] == api_key:
            print("✅ API Key loaded correctly")
        else:
            print("❌ API Key not loaded correctly")
            return False
            
        if X_CONFIG['API_SECRET'] == api_secret:
            print("✅ API Secret loaded correctly")
        else:
            print("❌ API Secret not loaded correctly")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_x_service_import():
    """Test X service import"""
    print("\n🚀 Testing X Service Import...")
    
    try:
        from Social_media_platforms.x_service import XService
        print("✅ XService imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import XService: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_x_service_initialization():
    """Test X service initialization (without making API calls)"""
    print("\n🔧 Testing X Service Initialization...")
    
    try:
        from Social_media_platforms.x_service import XService
        
        # Test with dummy tokens (won't make actual API calls)
        dummy_access_token = "dummy_access_token"
        dummy_access_token_secret = "dummy_access_token_secret"
        
        x_service = XService(dummy_access_token, dummy_access_token_secret)
        print("✅ XService initialized successfully")
        print(f"   Access Token: {x_service.access_token[:10]}...")
        print(f"   Access Token Secret: {x_service.access_token_secret[:10]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Standalone X Service Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_x_config()
    
    # Test service import
    import_ok = test_x_service_import()
    
    # Test service initialization
    init_ok = test_x_service_initialization()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"   Configuration: {'✅' if config_ok else '❌'}")
    print(f"   Service Import: {'✅' if import_ok else '❌'}")
    print(f"   Service Initialization: {'✅' if init_ok else '❌'}")
    
    if all([config_ok, import_ok, init_ok]):
        print("\n✅ All tests passed! X service is properly configured.")
        print("\nNext steps:")
        print("1. Get your access token and access token secret from X")
        print("2. Set them as environment variables:")
        print("   $env:X_TEST_ACCESS_TOKEN='your_access_token'")
        print("   $env:X_TEST_ACCESS_TOKEN_SECRET='your_access_token_secret'")
        print("3. Run the full test with: python simple_x_test.py")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
    
    return all([config_ok, import_ok, init_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 