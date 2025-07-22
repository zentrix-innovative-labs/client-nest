# microservices/ai-service/common/deepseek_client.py

"""
Token-optimized DeepSeek API Client for the AI microservice.
Optimized for 1M token budget with efficient prompts and monitoring.
"""
import asyncio
import json
import random
import os
import time
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from django.conf import settings
from common.signals import ai_usage_logged

# --- Client Configuration & Constants ---
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com/v1"
REQUEST_TIMEOUT = 60  # seconds

# Token estimation configuration
CHARS_PER_TOKEN = 4  # Average characters per token for estimation

# --- Add a logger ---
logger = logging.getLogger(__name__)

# --- Token Budget Tracking ---
class TokenBudgetTracker:
    def __init__(self):
        self.daily_usage = 0
        self.total_usage = 0
        self.last_reset = datetime.now().date()
        self.budget = settings.TOKEN_BUDGET
    
    def check_budget(self, estimated_tokens: int) -> bool:
        """Check if we can afford this request"""
        today = datetime.now().date()
        
        # Reset daily counter if it's a new day
        if today != self.last_reset:
            self.daily_usage = 0
            self.last_reset = today
        
        # Check daily limit
        if self.daily_usage + estimated_tokens > self.budget['DAILY_LIMIT']:
            logger.warning(f"Daily token limit exceeded: {self.daily_usage}/{self.budget['DAILY_LIMIT']}")
            return False
        
        # Check total budget
        if self.total_usage + estimated_tokens > self.budget['TOTAL_TOKENS']:
            logger.error(f"Total token budget exceeded: {self.total_usage}/{self.budget['TOTAL_TOKENS']}")
            return False
        
        return True
    
    def record_usage(self, prompt_tokens: int, completion_tokens: int):
        """Record token usage"""
        total_tokens = prompt_tokens + completion_tokens
        self.daily_usage += total_tokens
        self.total_usage += total_tokens
        
        # Log usage levels
        daily_percentage = self.daily_usage / self.budget['DAILY_LIMIT']
        total_percentage = self.total_usage / self.budget['TOTAL_TOKENS']
        
        if daily_percentage > self.budget['WARNING_THRESHOLD']:
            logger.warning(f"Daily usage at {daily_percentage:.1%}: {self.daily_usage}/{self.budget['DAILY_LIMIT']}")
        
        if total_percentage > self.budget['WARNING_THRESHOLD']:
            logger.warning(f"Total usage at {total_percentage:.1%}: {self.total_usage}/{self.budget['TOTAL_TOKENS']}")
        
        logger.info(f"Token usage: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})")

# Global token tracker
token_tracker = TokenBudgetTracker()

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

class TokenBudgetExceededError(AIClientError):
    """Raised when token budget is exceeded."""
    pass

class DeepSeekClient:
    SYSTEM_PROMPT_MAX_LENGTH = 500
    USER_PROMPT_MAX_LENGTH = 300
    """
    A token-optimized, production-ready client for the DeepSeek API.
    Optimized for 1M token budget with efficient prompts and monitoring.
    """
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not configured.")
        
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ClientNest/1.0"
        })
        self.last_usage = {}  # Track most recent usage data

    def _optimize_prompt(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        """Optimize prompts to use fewer tokens"""
        # Shorten system prompt
        if len(system_prompt) > self.SYSTEM_PROMPT_MAX_LENGTH:
            system_prompt = system_prompt[:self.SYSTEM_PROMPT_MAX_LENGTH] + "..."
        if len(user_prompt) > self.USER_PROMPT_MAX_LENGTH:
            user_prompt = user_prompt[:self.USER_PROMPT_MAX_LENGTH] + "..."
        
        return system_prompt, user_prompt

    def _estimate_tokens(self, text: str) -> int:
        """Improved token estimation using multiple heuristics for better accuracy"""
        if not text:
            return 0
        
        # Basic character-based estimation
        char_estimate = len(text) // CHARS_PER_TOKEN
        
        # Word-based estimation (more accurate for natural language)
        words = text.split()
        # Average tokens per word is around 0.75 for English
        word_estimate = int(len(words) * 0.75)
        
        # Account for punctuation and special characters
        punctuation_count = sum(1 for char in text if char in '.,!?;:()[]{}"\'')
        punctuation_tokens = punctuation_count // 2  # Rough estimate
        
        # Use the maximum of the estimates for safety
        return max(char_estimate, word_estimate + punctuation_tokens)

    def _parse_ai_response(self, raw_content: str) -> Dict[str, Any]:
        """
        Parse AI response content, handling markdown code blocks and JSON extraction.
        
        Args:
            raw_content: Raw content from AI response
            
        Returns:
            Parsed JSON content or fallback structure
        """
        # Handle responses wrapped in markdown code blocks
        if raw_content.startswith("```json"):
            raw_content = raw_content.replace("```json", "").replace("```", "").strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content.replace("```", "").strip()
        
        # Try to parse as JSON
        try:
            content_payload = json.loads(raw_content)
            return content_payload
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            import re
            
            # First try to find JSON between markdown code blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_content, re.DOTALL)
            if json_match:
                try:
                    content_payload = json.loads(json_match.group(1))
                    return content_payload
                except json.JSONDecodeError:
                    pass
            
            # Try to find any JSON object in the content
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_content, re.DOTALL)
            if json_match:
                try:
                    content_payload = json.loads(json_match.group())
                    return content_payload
                except json.JSONDecodeError:
                    pass
            
            # If still no valid JSON, return a structured fallback
            logger.warning(f"Could not parse JSON from AI response. Raw content: {raw_content[:200]}...")
            return {
                "error": "AI response could not be parsed as JSON",
                "raw_content": raw_content[:500],
                "fallback": True
            }

    def generate_content(self, system_prompt: str, user_prompt: str, user: Optional[settings.AUTH_USER_MODEL] = None, **kwargs) -> Dict[str, Any]:
        """
        Generates content using the DeepSeek API with token optimization.
        """
        # Optimize prompts for token efficiency
        if settings.CONTENT_GENERATION.get('OPTIMIZE_PROMPTS', True):
            system_prompt, user_prompt = self._optimize_prompt(system_prompt, user_prompt)
        
        # Estimate token usage
        estimated_tokens = self._estimate_tokens(system_prompt + user_prompt) + settings.CONTENT_GENERATION['MAX_TOKENS_PER_REQUEST']
        
        # Check budget before making request
        if not token_tracker.check_budget(estimated_tokens):
            raise TokenBudgetExceededError("Token budget exceeded. Please try again later.")
        
        endpoint = "/chat/completions"
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": kwargs.get("temperature", 0.8),
            "max_tokens": settings.CONTENT_GENERATION['MAX_TOKENS_PER_REQUEST'],
            "stream": False
        }

        start_time = time.perf_counter()
        
        try:
            response = self.session.post(
                f"{BASE_URL}{endpoint}",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            response_data = response.json()
            
            # Record token usage
            usage_data = response_data.get("usage", {})
            token_tracker.record_usage(
                usage_data.get("prompt_tokens", 0),
                usage_data.get("completion_tokens", 0)
            )
            
            # Store last usage for external access
            self.last_usage = usage_data
            
            self._log_usage(
                user=user,
                request_type="content_generation",
                usage_data=usage_data,
                response_time_ms=response_time_ms
            )

            # Parse response
            raw_content = response_data["choices"][0]["message"]["content"]
            return self._parse_ai_response(raw_content)
                    
        except (KeyError, IndexError) as e:
                logger.error(f"Failed to extract content from AI response. Error: {e}")
                raise AIAPIError(f"Failed to extract content from AI response. Missing key or index: {e}")

        except requests.exceptions.Timeout:
            raise AIConnectionError(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
        except requests.exceptions.RequestException as e:
            raise AIConnectionError(f"API request failed: {e}")
        except AIAPIError:
            raise
        except AIClientError:
            raise
        except Exception as e:
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

    def analyze_sentiment(self, text: str, user: Optional[settings.AUTH_USER_MODEL] = None, **kwargs) -> Dict[str, Any]:
        """
        Analyzes sentiment with optimized token usage.
        """
        # Use very short prompts for sentiment analysis
        system_prompt = "Analyze sentiment. Return ONLY valid JSON without any markdown formatting or code blocks: sentiment (positive/negative/neutral), confidence (0-1), emotions (array), urgency (low/medium/high), suggested_response_tone (string)."
        
        # Truncate text if too long
        if len(text) > 200:
            text = text[:200] + "..."
        
        # Estimate tokens
        estimated_tokens = self._estimate_tokens(system_prompt + text) + 200
        
        # Check budget
        if not token_tracker.check_budget(estimated_tokens):
            raise TokenBudgetExceededError("Token budget exceeded for sentiment analysis.")
        
        endpoint = "/chat/completions"
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": 200,  # Reduced for sentiment analysis
            "stream": False
        }
        
        start_time = time.perf_counter()
        try:
            response = self.session.post(
                f"{BASE_URL}{endpoint}",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            response_time_ms = int((time.perf_counter() - start_time) * 1000)
            response_data = response.json()
            
            # Record usage
            usage_data = response_data.get("usage", {})
            token_tracker.record_usage(
                usage_data.get("prompt_tokens", 0),
                usage_data.get("completion_tokens", 0)
            )
            
            # Store last usage for external access
            self.last_usage = usage_data
            
            self._log_usage(
                user=user,
                request_type="sentiment_analysis",
                usage_data=usage_data,
                response_time_ms=response_time_ms
            )
            
            raw_content = response_data["choices"][0]["message"]["content"]
            return self._parse_ai_response(raw_content)
                    
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from AI sentiment response. Error: {e}")
            raise AIAPIError(f"Failed to extract content from AI response. Missing key or index: {e}")
        except requests.exceptions.Timeout:
            raise AIConnectionError(f"Request timed out after {REQUEST_TIMEOUT} seconds.")
        except requests.exceptions.RequestException as e:
            raise AIConnectionError(f"API request failed: {e}")
        except AIAPIError:
            raise
        except AIClientError:
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in DeepSeekClient (sentiment): {e}")
            raise AIClientError(f"An unexpected error occurred: {e}")

    def get_token_usage(self) -> Dict[str, Any]:
        """Get current token usage statistics"""
        return {
            'daily_usage': token_tracker.daily_usage,
            'total_usage': token_tracker.total_usage,
            'daily_limit': token_tracker.budget['DAILY_LIMIT'],
            'total_budget': token_tracker.budget['TOTAL_TOKENS'],
            'daily_percentage': token_tracker.daily_usage / token_tracker.budget['DAILY_LIMIT'],
            'total_percentage': token_tracker.total_usage / token_tracker.budget['TOTAL_TOKENS'],
        } 