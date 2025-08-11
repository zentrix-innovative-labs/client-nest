#!/usr/bin/env python3
"""
AI Service Test Script
Run this script to test all AI service functionality
"""

import os
import sys
import django

from content_generation.logic import ContentGenerator
from common.deepseek_client import DeepSeekClient

def test_content_generation():
    """Test content generation for different platforms and tones"""
    print("🤖 AI Service Test Suite")
    print("=" * 50)
    
    # Initialize client and generator
    try:
        client = DeepSeekClient()
        generator = ContentGenerator(client)
        print("✅ DeepSeek client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return False
    
    test_results = []
    
    # Test 1: LinkedIn Professional Post
    print("\n📝 Test 1: LinkedIn Professional Post")
    print("-" * 40)
    try:
        result = generator.generate_post(
            topic="AI in business",
            platform="linkedin",
            user=None,
            tone="professional"
        )
        print(f"✅ Content: {result['content'][:100]}...")
        print(f"✅ Hashtags: {result['hashtags']}")
        print(f"✅ Quality Score: {result['quality_score']}")
        print(f"✅ Call to Action: {result['call_to_action']}")
        
        # Assertions
        assert 'content' in result, "Content field missing"
        assert 'hashtags' in result, "Hashtags field missing"
        assert 'quality_score' in result, "Quality score missing"
        assert isinstance(result['content'], str), "Content should be string"
        assert isinstance(result['hashtags'], list), "Hashtags should be list"
        test_results.append(True)
    except Exception as e:
        print(f"❌ Error: {e}")
        test_results.append(False)
    
    # Test 2: Twitter Casual Post
    print("\n🐦 Test 2: Twitter Casual Post")
    print("-" * 40)
    try:
        result = generator.generate_post(
            topic="Remote work tips",
            platform="twitter",
            user=None,
            tone="casual"
        )
        print(f"✅ Content: {result['content']}")
        print(f"✅ Hashtags: {result['hashtags']}")
        print(f"✅ Quality Score: {result['quality_score']}")
        
        # Assertions
        assert 'content' in result, "Content field missing"
        assert isinstance(result['content'], str), "Content should be string"
        test_results.append(True)
    except Exception as e:
        print(f"❌ Error: {e}")
        test_results.append(False)
    
    # Test 3: Instagram Inspirational Post
    print("\n📸 Test 3: Instagram Inspirational Post")
    print("-" * 40)
    try:
        result = generator.generate_post(
            topic="Healthy eating habits",
            platform="instagram",
            user=None,
            tone="inspirational"
        )
        print(f"✅ Content: {result['content']}")
        print(f"✅ Hashtags: {result['hashtags']}")
        print(f"✅ Call to Action: {result['call_to_action']}")
        
        # Assertions
        assert 'content' in result, "Content field missing"
        assert 'call_to_action' in result, "Call to action missing"
        test_results.append(True)
    except Exception as e:
        print(f"❌ Error: {e}")
        test_results.append(False)
    
    # Test 4: Facebook Friendly Post
    print("\n📘 Test 4: Facebook Friendly Post")
    print("-" * 40)
    try:
        result = generator.generate_post(
            topic="Small business marketing",
            platform="facebook",
            user=None,
            tone="friendly"
        )
        print(f"✅ Content: {result['content'][:100]}...")
        print(f"✅ Hashtags: {result['hashtags']}")
        print(f"✅ Variations: {len(result['variations'])} variations")
        
        # Assertions
        assert 'content' in result, "Content field missing"
        assert 'variations' in result, "Variations field missing"
        assert isinstance(result['variations'], list), "Variations should be list"
        test_results.append(True)
    except Exception as e:
        print(f"❌ Error: {e}")
        test_results.append(False)
    
    # Test 5: Sentiment Analysis
    print("\n🧠 Test 5: Sentiment Analysis")
    print("-" * 40)
    try:
        text = "I'm really excited about the new AI features in our product! The team has done an amazing job."
        sentiment_result = client.analyze_sentiment(text)
        print(f"✅ Text: {text}")
        print(f"✅ Sentiment: {sentiment_result['sentiment']}")
        print(f"✅ Confidence: {sentiment_result['confidence']}")
        print(f"✅ Emotions: {sentiment_result['emotions']}")
        
        # Assertions
        assert 'sentiment' in sentiment_result, "Sentiment field missing"
        assert 'confidence' in sentiment_result, "Confidence field missing"
        assert isinstance(sentiment_result['sentiment'], str), "Sentiment should be string"
        test_results.append(True)
    except Exception as e:
        print(f"❌ Error: {e}")
        test_results.append(False)
    
    # Test 6: Different Tones
    print("\n🎭 Test 6: Different Tones for Same Topic")
    print("-" * 40)
    tones = ["professional", "casual", "inspirational", "witty"]
    topic = "Digital transformation"
    
    for tone in tones:
        try:
            result = generator.generate_post(
                topic=topic,
                platform="linkedin",
                user=None,
                tone=tone
            )
            print(f"✅ {tone.title()}: {result['content'][:80]}...")
            print(f"   Quality Score: {result['quality_score']}")
            
            # Assertions
            assert 'content' in result, f"Content field missing for {tone}"
            assert 'quality_score' in result, f"Quality score missing for {tone}"
        except Exception as e:
            print(f"❌ {tone.title()}: Error - {e}")
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n🎉 Test Suite Completed!")
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    print("=" * 50)
    
    return passed_tests == total_tests

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("\n🌐 Testing API Endpoints")
    print("-" * 40)
    
    import requests
    
    base_url = "http://localhost:8005"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/api/health/")
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on port 8005")
    except Exception as e:
        print(f"❌ Error testing health check: {e}")

if __name__ == "__main__":
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
    django.setup()
    
    # Check for required environment variables
    required_vars = [
        'DEEPSEEK_API_KEY',
        'SECRET_KEY',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT'
    ]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment:")
        for var in missing_vars:
            if var == 'DEEPSEEK_API_KEY':
                print(f"  {var}=your-actual-deepseek-api-key")
            elif var == 'SECRET_KEY':
                print(f"  {var}=your-secure-django-secret-key")
            elif var.startswith('DB_'):
                print(f"  {var}=your-database-{var.lower()}")
        sys.exit(1)
    
    # Set optional defaults
    if not os.environ.get('DEBUG'):
        os.environ['DEBUG'] = "True"
    
    # Run tests
    content_test_passed = test_content_generation()
    test_api_endpoints()
    
    if content_test_passed:
        print("✅ All content generation tests passed!")
    else:
        print("❌ Some content generation tests failed!")
        sys.exit(1) 