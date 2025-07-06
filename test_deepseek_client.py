#!/usr/bin/env python3
"""
Test script for DeepSeek client functionality.
Run this script to test the AI client without Django.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the ai_services path to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_services_path = os.path.join(current_dir, 'ai_services')
if ai_services_path not in sys.path:
    sys.path.insert(0, ai_services_path)

def test_deepseek_client():
    """Test the DeepSeek client functionality."""
    
    # Check for required environment variables
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable is not set.")
        logger.info("Please set it with: $env:OPENROUTER_API_KEY='your-api-key'")
        return False
    
    try:
        # Import the client
        from ai_services.common.deepseek_client import DeepSeekClient, AIClientError
        
        # Create client instance
        logger.info("Creating DeepSeek client...")
        client = DeepSeekClient(api_key=api_key)
        logger.info("✓ DeepSeek client created successfully")
        
        # Test content generation
        logger.info("Testing content generation...")
        result = client.generate_content(
            system_prompt="You are a helpful assistant that creates engaging social media content.",
            user_prompt="Write a short, engaging post about artificial intelligence for LinkedIn.",
            user=None,  # No user for testing
            model="deepseek/deepseek-r1-0528:free",
            temperature=0.8,
            max_tokens=200
        )
        
        logger.info("✓ Content generation successful!")
        logger.info(f"Generated content: {result}")
        
        return True
        
    except AIClientError as e:
        logger.error(f"AI client error: {e}")
        return False
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure you're running this script from the project root directory.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    """Main function to run the test."""
    logger.info("Starting DeepSeek client test...")
    
    success = test_deepseek_client()
    
    if success:
        logger.info("🎉 All tests passed! DeepSeek client is working correctly.")
    else:
        logger.error("❌ Tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 