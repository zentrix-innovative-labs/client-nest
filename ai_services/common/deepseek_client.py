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
from typing import Dict, Any, Optional
import sys

# --- Logging for debugging import path and environment ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"sys.path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Contents of current directory: {os.listdir(os.getcwd())}")
logger.info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

from django.conf import settings
from client_nest.ai_services.common.signals import ai_usage_logged

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
    ) -> Dict[str, Any]:
        """
        Generates content using the DeepSeek API via OpenRouter and logs the usage.
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

            self._log_usage(
                user=user,
                request_type="content_generation",
                usage_data=response_data.get("usage", {}),
                response_time_ms=response_time_ms
            )

            # Safely extract and parse the AI content
            choices = response_data.get("choices", [])
            if not choices:
                raise AIAPIError("No choices returned by the AI response.")
            raw_content = choices[0].get("message", {}).get("content")
            if not raw_content:
                raise AIAPIError("No message content found in AI response.")

            return raw_content

        except requests.exceptions.Timeout:
            raise AIConnectionError(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
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
            ai_usage_logged.send(
                sender=self.__class__,
                user=user,
                request_type=request_type,
                usage_data=usage_data,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.warning(f"Failed to log AI usage: {e}")

# --- Local Test Mode ---
def main():
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.error("Please set the OPENROUTER_API_KEY environment variable.")
        return

    class MockUser:
        username = "testuser"

    def mock_ai_usage_logged(*args, **kwargs):
        logger.info("Mock usage logged: %s %s", args, kwargs)

    try:
        from client_nest.ai_services.common import signals
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
