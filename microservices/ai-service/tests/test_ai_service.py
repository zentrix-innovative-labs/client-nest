#!/usr/bin/env python3
"""
AI Service Test Script
Run this script to test all AI service functionality
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
django.setup()

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
        return
    
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
    except Exception as e:
        print(f"❌ Error: {e}")
    
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
    except Exception as e:
        print(f"❌ Error: {e}")
    
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
    except Exception as e:
        print(f"❌ Error: {e}")
    
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
    except Exception as e:
        print(f"❌ Error: {e}")
    
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
    except Exception as e:
        print(f"❌ Error: {e}")
    
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
        except Exception as e:
            print(f"❌ {tone.title()}: Error - {e}")
    
    print("\n🎉 Test Suite Completed!")
    print("=" * 50)

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
    # Set environment variables if not already set
    if not os.environ.get('DEEPSEEK_API_KEY'):
        os.environ['DEEPSEEK_API_KEY'] = "sk-54e218fd7ca14f698a9e65e8678dd92b"
    
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = "django-insecure-ai-service-key"
    
    if not os.environ.get('DEBUG'):
        os.environ['DEBUG'] = "True"
    
    # Run tests
    test_content_generation()
    test_api_endpoints() 