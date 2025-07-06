"""
Production-ready DeepSeek API Client using OpenRouter as the backend.
Implements robust error handling, logging, and usage tracking.
Uses OpenRouter's free API key for cost-free development and testing.
Maintainer: Onyait Elias
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, Union
import sys

# --- Logging setup (library-friendly) ---
logger = logging.getLogger(__name__)

DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production").lower()
if DEBUG and ENVIRONMENT == "development":
    logger.info("Running in debug mode in a development environment.")
    logger.info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    # Detailed environment and file listings have been omitted to avoid exposing sensitive data.

# --- Configuration ---
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
REQUEST_TIMEOUT = 30  # seconds
SUPPORTED_MODELS = {"deepseek/deepseek-r1-0528:free"}

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
    Synchronous client for the DeepSeek API via OpenRouter.
    Includes error handling, logging, and usage tracking.
    """
    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")
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
        Generates content using the DeepSeek API via OpenRouter and logs the usage.
        Returns the generated content as a string.
        """
        model = kwargs.get("model", "deepseek/deepseek-r1-0528:free")
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

        logger.info(f"Payload being sent: {payload}")

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

            # Always log usage after a successful response
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
        Sends a signal to log the AI API usage.
        """
        try:
            # Try to import Django components safely
            from .signals import ai_usage_logged
            ai_usage_logged.send(
                sender=self.__class__,
                user=user,
                request_type=request_type,
                usage_data=usage_data,
                response_time_ms=response_time_ms
            )
        except ImportError:
            logger.warning("Django signals not available, skipping usage logging")
        except Exception as e:
            logger.warning(f"Failed to log AI usage: {e}")

# --- Local Test Mode ---
def main():
    # Set up Django environment if not already configured
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        User = get_user_model()
    except Exception as e:
        logger.warning(f"Django setup failed: {e}")
        User = None

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.error("Please set the OPENROUTER_API_KEY environment variable.")
        return

    class MockUser:
        username = "testuser"

    def mock_ai_usage_logged(*args, **kwargs):
        logger.info("Mock usage logged: %s %s", args, kwargs)

    try:
        from . import signals
        signals.ai_usage_logged = mock_ai_usage_logged
    except ImportError:
        pass

    client = DeepSeekClient(api_key=api_key)
    try:
        result = client.generate_content(
            system_prompt="You are a helpful assistant.",
            user_prompt="Write a short post about AI for social media.",
            user=MockUser(),
            model="deepseek/deepseek-r1-0528:free"
        )
        logger.info("AI Response: %s", result)
    except Exception as e:
        logger.error("Error during content generation: %s", e)

if __name__ == "__main__":
    main()
