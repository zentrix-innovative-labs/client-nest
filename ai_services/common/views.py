from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
import logging
from client_nest.ai_services.common.deepseek_client import DeepSeekClient, AIClientError, AIAPIError, AIConnectionError

# Get logger for this module
logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def generate_content_endpoint(request):
    """
    Generate AI content using DeepSeek API.
    Requires authentication and accepts POST requests only.
    """
    try:
        # Parse request data
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON format in request body.'
            }, status=400)
        
        # Validate required fields
        system_prompt = data.get('system_prompt', 'You are a helpful assistant.')
        user_prompt = data.get('user_prompt', '')
        
        if not user_prompt:
            return JsonResponse({
                'error': 'user_prompt is required and cannot be empty.'
            }, status=400)
        
        # Validate input lengths
        if len(user_prompt) > 4000:
            return JsonResponse({
                'error': 'user_prompt is too long. Maximum 4000 characters allowed.'
            }, status=400)
        
        if len(system_prompt) > 2000:
            return JsonResponse({
                'error': 'system_prompt is too long. Maximum 2000 characters allowed.'
            }, status=400)
        
        # Get optional parameters
        model = data.get('model', 'deepseek/deepseek-r1-0528:free')
        temperature = data.get('temperature', 0.8)
        max_tokens = data.get('max_tokens', 800)
        
        # Validate parameters
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            return JsonResponse({
                'error': 'temperature must be a number between 0 and 2.'
            }, status=400)
        
        if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 4000:
            return JsonResponse({
                'error': 'max_tokens must be an integer between 1 and 4000.'
            }, status=400)
        
        # Initialize client and generate content
        client = DeepSeekClient()
        result = client.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            user=request.user,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Return successful response
        return JsonResponse({
            'success': True,
            'result': result,
            'model': model,
            'parameters': {
                'temperature': temperature,
                'max_tokens': max_tokens
            }
        })
        
    except AIClientError as e:
        # Handle AI client specific errors
        logger.warning(f"AI client error for user {request.user.username}: {e}")
        return JsonResponse({
            'error': 'AI service error occurred.',
            'details': str(e)
        }, status=503)
        
    except AIAPIError as e:
        # Handle API-specific errors
        logger.warning(f"AI API error for user {request.user.username}: {e}")
        return JsonResponse({
            'error': 'AI API error occurred.',
            'details': str(e)
        }, status=502)
        
    except AIConnectionError as e:
        # Handle connection errors
        logger.warning(f"AI connection error for user {request.user.username}: {e}")
        return JsonResponse({
            'error': 'Unable to connect to AI service. Please try again later.',
            'details': str(e)
        }, status=503)
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in generate_content_endpoint for user {request.user.username}: {e}", exc_info=True)
        return JsonResponse({
            'error': 'An internal server error occurred. Please try again later.'
        }, status=500) 