# microservices/ai-service/content_generation/signals.py
from django.dispatch import Signal, receiver
from django.conf import settings
from .models import AIUsageLog
import logging
from django.db import DatabaseError
import decimal
from common.signals import ai_usage_logged

# --- Add a logger ---
logger = logging.getLogger(__name__)

# Decimal precision configuration for financial calculations
DECIMAL_PRECISION = 10  # Configurable precision for cost calculations

def _calculate_cost(prompt_tokens: int, completion_tokens: int) -> decimal.Decimal:
    """
    Calculates the cost of AI API usage based on DeepSeek's pricing model.
    
    This function uses Decimal for precision and a local context to ensure thread-safe 
    precision settings. It calculates the cost for prompt tokens and completion tokens 
    based on the pricing configuration provided in `settings.DEEPSEEK_PRICING`.
    
    Parameters:
        prompt_tokens (int): The number of tokens in the prompt. Must be a non-negative integer.
        completion_tokens (int): The number of tokens in the completion. Must be a non-negative integer.
    
    Returns:
        decimal.Decimal: The calculated cost, rounded to the configured precision.
    
    Raises:
        TypeError: If `prompt_tokens` or `completion_tokens` are not integers.
        ValueError: If `prompt_tokens` or `completion_tokens` are negative.
    """
    # Input validation
    if not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int):
        raise TypeError("Token counts must be integers")
    
    if prompt_tokens < 0 or completion_tokens < 0:
        raise ValueError("Token counts must be non-negative")
    
    with decimal.localcontext() as ctx:
        # Set precision for Decimal calculations within this context
        ctx.prec = DECIMAL_PRECISION

        # Prices per 1,000 tokens, as Decimal objects, from settings
        pricing = settings.DEEPSEEK_PRICING
        prompt_cost_per_1k = decimal.Decimal(str(pricing['prompt']))
        completion_cost_per_1k = decimal.Decimal(str(pricing['completion']))
        
        # Use Decimal for all calculations to avoid floating point inaccuracies
        prompt_cost = (decimal.Decimal(prompt_tokens) / decimal.Decimal(1000)) * prompt_cost_per_1k
        completion_cost = (decimal.Decimal(completion_tokens) / decimal.Decimal(1000)) * completion_cost_per_1k
        
        result = prompt_cost + completion_cost
        return result.quantize(decimal.Decimal('1.' + '0' * DECIMAL_PRECISION))

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