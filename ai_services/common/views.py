from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
import json
from client_nest.ai_services.common.deepseek_client import DeepSeekClient
import logging

@csrf_exempt
def generate_content_endpoint(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST requests are allowed.')
    try:
        data = json.loads(request.body.decode('utf-8'))
        system_prompt = data.get('system_prompt', 'You are a helpful assistant.')
        user_prompt = data.get('user_prompt', '')
        if not user_prompt:
            return JsonResponse({'error': 'user_prompt is required.'}, status=400)
        client = DeepSeekClient()
        result = client.generate_content(system_prompt, user_prompt)
        return JsonResponse({'result': result})
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        return JsonResponse({'error': 'An internal error occurred. Please try again later.'}, status=500) 