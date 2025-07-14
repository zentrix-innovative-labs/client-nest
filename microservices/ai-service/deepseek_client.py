"""
Production-ready DeepSeek API Client using direct DeepSeek API.
Implements robust error handling, logging, and usage tracking.
Uses DeepSeek's direct API for content generation.
Maintainer: Onyait Elias
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, Union
import sys
from decouple import config

# --- Logging setup (library-friendly) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production").lower()
if DEBUG and ENVIRONMENT == "development":
    logger.info("Running in debug mode in a development environment.")

# --- Configuration ---
DEEPSEEK_API_KEY = config('DEEPSEEK_API_KEY', default='')
BASE_URL = "https://api.deepseek.com/v1"
REQUEST_TIMEOUT = 30  # seconds
SUPPORTED_MODELS = {"deepseek-chat", "deepseek-coder"}

# --- Custom Exceptions ---
class AIClientError(Exception):
    """Base exception for AI client errors."""
    pass

class AIAPIError(AIClientError):
    """Represents an error returned by the AI API."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class AIConnectionError(AIClientError):
    """Represents a connection error to the AI API."""
    pass

# --- Main Client ---
class DeepSeekClient:
    """
    Synchronous client for the DeepSeek API.
    Includes error handling, logging, and usage tracking.
    """
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured. Please set it in your .env file.")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ClientNest/1.0"
        })

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        user: Optional[object] = None,
        **kwargs
    ) -> str:
        """
        Generates content using the DeepSeek API and logs the usage.
        Returns the generated content as a string.
        """
        model = kwargs.get("model", "deepseek-chat")
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model}")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": kwargs.get("temperature", 0.8),
            "max_tokens": kwargs.get("max_tokens", 800),
            "stream": False
        }

        logger.info(f"Sending request to DeepSeek API with model: {model}")

        start_time = time.perf_counter()
        try:
            response = self.session.post(
                f"{BASE_URL}/chat/completions",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            response_data = response.json()

            # Log usage information
            self._log_usage(
                user=user,
                request_type="content_generation",
                usage_data=response_data.get("usage", {}),
                response_time_ms=response_time_ms
            )

            # Now check for content
            choices = response_data.get("choices", [])
            if not choices:
                raise AIAPIError("No choices returned by the AI response.")
            raw_content = choices[0].get("message", {}).get("content")
            if not raw_content:
                raise AIAPIError("No message content found in AI response.")

            logger.info(f"Successfully generated content in {response_time_ms}ms")
            return raw_content

        except requests.exceptions.Timeout:
            raise AIConnectionError(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
        except requests.exceptions.HTTPError as e:
            raise AIAPIError(f"HTTP error occurred: {e.response.status_code} {e.response.reason}", status_code=e.response.status_code)
        except requests.exceptions.RequestException as e:
            raise AIConnectionError(f"API request failed: {e}")
        except AIClientError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in DeepSeekClient: {e}")
            raise AIClientError(f"Unexpected error: {e}")

    def _log_usage(self, user: Optional[object], request_type: str, usage_data: Dict[str, int], response_time_ms: int):
        """
        Logs the AI API usage information.
        """
        try:
            # Simple logging without Django signals
            usage_info = {
                "request_type": request_type,
                "usage_data": usage_data,
                "response_time_ms": response_time_ms,
                "user": getattr(user, 'username', 'unknown') if user else 'unknown'
            }
            logger.info(f"AI Usage logged: {usage_info}")
        except Exception as e:
            logger.warning(f"Failed to log AI usage: {e}")

# --- Local Test Mode ---
def main():
    """Test the DeepSeek client functionality."""
    
    # Check for API key
    api_key = config("DEEPSEEK_API_KEY", default='')
    if not api_key:
        logger.error("Please set the DEEPSEEK_API_KEY environment variable in your .env file.")
        logger.info("Example .env file content:")
        logger.info("DEEPSEEK_API_KEY=your-deepseek-api-key-here")
        return

    # Create a mock user for testing
    class MockUser:
        username = "testuser"

    # Test the client
    try:
        logger.info("Creating DeepSeek client...")
        client = DeepSeekClient(api_key=api_key)
        logger.info("✓ DeepSeek client created successfully")
        
        logger.info("Testing content generation...")
        result = client.generate_content(
            system_prompt="You are a helpful assistant that creates engaging social media content.",
            user_prompt="Write a short, engaging post about artificial intelligence for LinkedIn.",
            user=MockUser(),
            model="deepseek-chat",
            temperature=0.8,
            max_tokens=200
        )
        
        logger.info("✓ Content generation successful!")
        logger.info(f"Generated content: {result}")
        
    except AIClientError as e:
        logger.error(f"AI client error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
