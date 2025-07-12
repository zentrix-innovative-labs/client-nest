#!/usr/bin/env python3
"""
Interactive AI Service Test Interface
Run this for an interactive testing experience
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
django.setup()

from content_generation.logic import ContentGenerator
from common.deepseek_client import DeepSeekClient

def setup_environment():
    """Set up environment variables"""
    # Check for required environment variables
    required_vars = ['DEEPSEEK_API_KEY', 'SECRET_KEY']
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
        return False
    
    # Set optional defaults
    if not os.environ.get('DEBUG'):
        os.environ['DEBUG'] = "True"
    
    return True

def initialize_ai_service():
    """Initialize the AI service components"""
    try:
        client = DeepSeekClient()
        generator = ContentGenerator(client)
        print("✅ AI Service initialized successfully!")
        return client, generator
    except Exception as e:
        print(f"❌ Error initializing AI service: {e}")
        return None, None

def test_content_generation(client, generator):
    """Interactive content generation test"""
    print("\n🎯 Content Generation Test")
    print("=" * 40)
    
    # Get user input
    topic = input("Enter topic (or press Enter for default 'AI in business'): ").strip()
    if not topic:
        topic = "AI in business"
    
    platform = input("Enter platform (linkedin/twitter/instagram/facebook) [linkedin]: ").strip().lower()
    if not platform:
        platform = "linkedin"
    
    tone = input("Enter tone (professional/casual/inspirational/witty) [professional]: ").strip().lower()
    if not tone:
        tone = "professional"
    
    print(f"\n🔄 Generating content for '{topic}' on {platform} with {tone} tone...")
    
    try:
        result = generator.generate_post(
            topic=topic,
            platform=platform,
            user=None,
            tone=tone
        )
        
        print("\n✅ Generated Content:")
        print("-" * 30)
        
        # Handle different response structures
        if isinstance(result, dict):
            # Check for different possible response formats
            if 'content' in result:
                print(f"📝 Content: {result['content']}")
            elif 'text' in result:
                print(f"📝 Content: {result['text']}")
            elif 'message' in result:
                print(f"📝 Content: {result['message']}")
            else:
                print(f"📝 Content: {result}")
            
            if 'hashtags' in result:
                print(f"🏷️  Hashtags: {result['hashtags']}")
            if 'call_to_action' in result:
                print(f"📞 Call to Action: {result['call_to_action']}")
            if 'quality_score' in result:
                print(f"⭐ Quality Score: {result['quality_score']}")
            
            if 'variations' in result and result['variations']:
                print(f"🔄 Variations: {len(result['variations'])} available")
                show_variations = input("\nShow variations? (y/n): ").strip().lower()
                if show_variations == 'y':
                    for i, variation in enumerate(result['variations'], 1):
                        print(f"\nVariation {i}: {variation}")
        else:
            print(f"📝 Response: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        print(f"Response type: {type(result) if 'result' in locals() else 'Not available'}")
        if 'result' in locals() and result is not None:
            print(f"Response structure: {result}")
        return None

def test_sentiment_analysis(client):
    """Interactive sentiment analysis test"""
    print("\n🧠 Sentiment Analysis Test")
    print("=" * 40)
    
    text = input("Enter text to analyze (or press Enter for default): ").strip()
    if not text:
        text = "I'm really excited about the new AI features in our product! The team has done an amazing job."
    
    print(f"\n🔄 Analyzing sentiment for: '{text}'")
    
    try:
        result = client.analyze_sentiment(text)
        
        print("\n✅ Sentiment Analysis Results:")
        print("-" * 30)
        print(f"😊 Sentiment: {result['sentiment']}")
        print(f"🎯 Confidence: {result['confidence']}")
        print(f"💭 Emotions: {result['emotions']}")
        print(f"⚡ Urgency: {result['urgency']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error analyzing sentiment: {e}")
        return None

def main_menu():
    """Main interactive menu"""
    print("🤖 AI Service Interactive Test Interface")
    print("=" * 50)
    
    # Initialize AI service
    client, generator = initialize_ai_service()
    if not client or not generator:
        return
    
    while True:
        print("\n📋 Available Tests:")
        print("1. 🎯 Test Content Generation")
        print("2. 🧠 Test Sentiment Analysis")
        print("3. 🚀 Quick Test (All Features)")
        print("4. ❌ Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            test_content_generation(client, generator)
        elif choice == '2':
            test_sentiment_analysis(client)
        elif choice == '3':
            quick_test(client, generator)
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")

def quick_test(client, generator):
    """Run a quick test of all features"""
    print("\n🚀 Quick Test - All Features")
    print("=" * 40)
    
    # Test 1: LinkedIn Professional
    print("\n📝 Testing LinkedIn Professional...")
    try:
        result = generator.generate_post(
            topic="Digital transformation",
            platform="linkedin",
            user=None,
            tone="professional"
        )
        quality_score = result.get('quality_score', 'N/A') if isinstance(result, dict) else 'N/A'
        print(f"✅ LinkedIn: Quality Score {quality_score}")
    except Exception as e:
        print(f"❌ LinkedIn Error: {e}")
    
    # Test 2: Twitter Casual
    print("\n🐦 Testing Twitter Casual...")
    try:
        result = generator.generate_post(
            topic="Remote work",
            platform="twitter",
            user=None,
            tone="casual"
        )
        quality_score = result.get('quality_score', 'N/A') if isinstance(result, dict) else 'N/A'
        print(f"✅ Twitter: Quality Score {quality_score}")
    except Exception as e:
        print(f"❌ Twitter Error: {e}")
    
    # Test 3: Sentiment Analysis
    print("\n🧠 Testing Sentiment Analysis...")
    try:
        result = client.analyze_sentiment("I love this new AI service!")
        print(f"✅ Sentiment: {result['sentiment']} (Confidence: {result['confidence']})")
    except Exception as e:
        print(f"❌ Sentiment Error: {e}")
    
    print("\n🎉 Quick test completed!")

if __name__ == "__main__":
    if setup_environment():
        main_menu()
    else:
        print("❌ Cannot start without required environment variables.")
        sys.exit(1) 