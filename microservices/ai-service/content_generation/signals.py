# microservices/ai-service/content_generation/signals.py
import os
from django.dispatch import Signal, receiver
from django.conf import settings
from .models import AIUsageLog
import logging
from django.db import DatabaseError
import decimal
from common.signals import ai_usage_logged
from typing import TypedDict

# --- Add a logger ---
logger = logging.getLogger(__name__)

# Decimal precision configuration for financial calculations
DECIMAL_PRECISION = 10  # Configurable precision for cost calculations
QUANTIZATION_PATTERN = decimal.Decimal('1.' + '0' * DECIMAL_PRECISION)

class DeepSeekPricing(TypedDict):
    prompt: float
    completion: float

# Module-level constants for performance optimization
# These are loaded once at module import time rather than on every function call
MAX_PROMPT_TOKENS = int(os.environ.get('MAX_PROMPT_TOKENS_VALIDATION', '1000000'))  # Configurable via env var
MAX_COMPLETION_TOKENS = int(os.environ.get('MAX_COMPLETION_TOKENS_VALIDATION', '1000000'))  # Configurable via env var
ENABLE_TOKEN_VALIDATION = os.environ.get('ENABLE_TOKEN_VALIDATION', 'true').lower() == 'true'

def _calculate_cost(prompt_tokens: int, completion_tokens: int) -> decimal.Decimal:
    """
    Calculates the cost of AI API usage based on DeepSeek's pricing model.
    
    This function uses Decimal for precision and a local context to ensure thread-safe 
    precision settings. It calculates the cost for prompt tokens and completion tokens 
    based on the pricing configuration provided in `settings.DEEPSEEK_PRICING`.
    
    Performance optimized with configurable validation that can be disabled in production.
    
    Parameters:
        prompt_tokens (int): Number of prompt tokens.
        completion_tokens (int): Number of completion tokens.
    Settings:
        settings.DEEPSEEK_PRICING (DeepSeekPricing): Pricing dictionary with 'prompt' and 'completion' keys.
        MAX_PROMPT_TOKENS_VALIDATION: Environment variable for max prompt tokens (default: 1M)
        MAX_COMPLETION_TOKENS_VALIDATION: Environment variable for max completion tokens (default: 1M)
        ENABLE_TOKEN_VALIDATION: Environment variable to enable/disable validation (default: true)
    
    Returns:
        decimal.Decimal: The calculated cost, rounded to the configured precision.
    
    Raises:
        TypeError: If `prompt_tokens` or `completion_tokens` are not integers.
        ValueError: If `prompt_tokens` or `completion_tokens` are negative or exceed maximum limits.
    
    Example:
        >>> _calculate_cost(1000, 2000)
        Decimal('0.0050000000')
    """
    # Lightweight validation - only perform expensive checks if enabled
    if ENABLE_TOKEN_VALIDATION:
        # Type validation
        if not all(isinstance(token, int) for token in (prompt_tokens, completion_tokens)):
            raise TypeError("Token counts must be integers")
        
        # Range validation
        if prompt_tokens < 0 or completion_tokens < 0:
            raise ValueError("Token counts must be non-negative")
        
        # Maximum bounds validation - using module-level constants for performance
        if prompt_tokens > MAX_PROMPT_TOKENS:
            raise ValueError(f"Prompt tokens ({prompt_tokens}) exceed maximum limit ({MAX_PROMPT_TOKENS})")
        
        if completion_tokens > MAX_COMPLETION_TOKENS:
            raise ValueError(f"Completion tokens ({completion_tokens}) exceed maximum limit ({MAX_COMPLETION_TOKENS})")
    
    with decimal.localcontext() as ctx:
        # Set precision for Decimal calculations within this context
        ctx.prec = DECIMAL_PRECISION

        # Prices per 1,000 tokens, as Decimal objects, from settings
        pricing = settings.DEEPSEEK_PRICING
        prompt_cost_per_1k = decimal.Decimal(str(pricing['prompt']))
        completion_cost_per_1k = decimal.Decimal(str(pricing['completion']))
        
        # Calculate total cost in a single expression for better readability
        total_cost = ((decimal.Decimal(prompt_tokens) / decimal.Decimal(1000)) * prompt_cost_per_1k) + \
                     ((decimal.Decimal(completion_tokens) / decimal.Decimal(1000)) * completion_cost_per_1k)
        
        return total_cost.quantize(QUANTIZATION_PATTERN)

@receiver(ai_usage_logged)
def log_ai_usage_receiver(sender, **kwargs):
    """
    Receives a signal to log AI API usage to the database.
    """
    user = kwargs.get("user")
    request_type = kwargs.get("request_type")
    usage_data = kwargs.get("usage_data", {})
    response_time_ms = kwargs.get("response_time_ms")

    prompt_tokens = usage_data.get("prompt_tokens", 0)
    completion_tokens = usage_data.get("completion_tokens", 0)
    
    cost = _calculate_cost(prompt_tokens, completion_tokens)

    try:
        AIUsageLog.objects.create(
            user=user,
            request_type=request_type,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage_data.get("total_tokens", 0),
            cost=cost,
            response_time_ms=response_time_ms
        )
    except DatabaseError as e:
        logger.error(f"Database error while logging AI usage: {e}") 