from django.dispatch import Signal, receiver
from decimal import Decimal, getcontext
from .models import AIUsageLog


ai_usage_logged = Signal()

def _calculate_cost(prompt_tokens: int, completion_tokens: int) -> Decimal:
    """
    Calculates the cost based on DeepSeek's pricing model using Decimal for precision.
    """
    # Set precision for Decimal calculations
    getcontext().prec = 10

    # Prices per 1,000 tokens, as Decimal objects
    prompt_cost_per_1k = Decimal('0.0014')
    completion_cost_per_1k = Decimal('0.0028')
    
    # Use Decimal for all calculations to avoid floating point inaccuracies
    prompt_cost = (Decimal(prompt_tokens) / Decimal(1000)) * prompt_cost_per_1k
    completion_cost = (Decimal(completion_tokens) / Decimal(1000)) * completion_cost_per_1k
    
    return prompt_cost + completion_cost

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

    AIUsageLog.objects.create(
        user=user,
        request_type=request_type,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=usage_data.get("total_tokens", 0),
        cost=cost,
        response_time_ms=response_time_ms
    ) 