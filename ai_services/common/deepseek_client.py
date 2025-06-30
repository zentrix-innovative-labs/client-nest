# ai_services/common/deepseek_client.py

"""
Mock/Placeholder for the DeepSeek API Client.
Onyait Elias is responsible for the final implementation.
This mock allows Denzel's code to be developed and tested in isolation.
"""
import asyncio
import json
import random
import os
import time
import requests
import logging
from typing import Dict, Any, Optional

from django.conf import settings
from ai_services.common.signals import ai_usage_logged

# --- Client Configuration & Constants ---
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your-deepseek-api-key-goes-here")
BASE_URL = "https://api.deepseek.com/v1"
REQUEST_TIMEOUT = 30  # seconds

# --- Add a logger ---
logger = logging.getLogger(__name__)

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

class DeepSeekClient:
    """
    A production-ready, synchronous client for the DeepSeek API.
    This implementation fulfills Onyait Elias's core task of building a robust API client.
    It includes error handling and cost/usage tracking.
    """
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        if not api_key or "your-deepseek-api-key" in api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured.")
        
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ClientNest/1.0"
        })

    def generate_content(self, system_prompt: str, user_prompt: str, user: Optional[settings.AUTH_USER_MODEL] = None, **kwargs) -> Dict[str, Any]:
        """
        Generates content using the DeepSeek API and logs the usage.
        """
        endpoint = "/chat/completions"
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": kwargs.get("temperature", 0.8),
            "max_tokens": kwargs.get("max_tokens", 800),
            "stream": False
        }

        start_time = time.perf_counter()
        
        try:
            response = self.session.post(
                f"{BASE_URL}{endpoint}",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            
            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            response_data = response.json()
            
            self._log_usage(
                user=user,
                request_type="content_generation",
                usage_data=response_data.get("usage", {}),
                response_time_ms=response_time_ms
            )

            # The actual content is a JSON string, so we parse it.
            raw_content = None
            try:
                # Note: The AI is expected to return a JSON string as the message content
                raw_content = response_data["choices"][0]["message"]["content"]
                content_payload = json.loads(raw_content)
                return content_payload
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.error(
                    f"Failed to parse JSON from AI response. "
                    f"Raw content: '{raw_content if raw_content is not None else 'Not Available'}'. Error: {e}"
                )
                raise AIAPIError("Failed to parse valid content from AI response.")

        except requests.exceptions.Timeout:
            raise AIConnectionError(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
        except requests.exceptions.RequestException as e:
            raise AIConnectionError(f"API request failed: {e}")
        except AIAPIError:
            # Re-raise AIAPIError to preserve its specific meaning.
            raise
        except AIClientError:
            # Re-raise AIClientError for the same reason.
            raise
        except Exception as e:
            # Catch-all for other unexpected errors.
            logger.error(f"An unexpected error occurred in DeepSeekClient: {e}")
            raise AIClientError(f"An unexpected error occurred: {e}")

    def _log_usage(self, user: Optional[settings.AUTH_USER_MODEL], request_type: str, usage_data: Dict[str, int], response_time_ms: int):
        """
        Sends a signal to log the AI API usage.
        """
        ai_usage_logged.send(
            sender=self.__class__,
            user=user,
            request_type=request_type,
            usage_data=usage_data,
            response_time_ms=response_time_ms
        ) 