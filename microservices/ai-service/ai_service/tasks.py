from celery import shared_task
from django.conf import settings
import requests
import json
from content_generation.prompts import get_base_system_prompt, get_user_prompt

@shared_task
def generate_content_task(topic, platform='general', tone='professional'):
    system_prompt = get_base_system_prompt(platform, tone)
    user_prompt = get_user_prompt(topic, 'post')
    payload = {
        "model": settings.AI_MODELS['DEEPSEEK']['MODEL_NAME'],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": settings.AI_MODELS['DEEPSEEK']['TEMPERATURE'],
        "max_tokens": 800,
        "stream": False
    }
    response = requests.post(
        f"{settings.AI_MODELS['DEEPSEEK']['BASE_URL']}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.AI_MODELS['DEEPSEEK']['API_KEY']}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    raw_content = data["choices"][0]["message"]["content"]
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as e:
        return {
            "error": "Invalid JSON content returned by the AI service.",
            "details": str(e),
            "raw_content": raw_content
        }

@shared_task
def sentiment_analysis_task(text):
    system_prompt = (
        "You are a sentiment analysis expert. Analyze the sentiment of the given text. "
        "Return a JSON object with keys: sentiment (positive, negative, neutral), confidence (0-1), emotions (array), urgency (low, medium, high), suggested_response_tone (string)."
    )
    payload = {
        "model": settings.AI_MODELS['DEEPSEEK']['MODEL_NAME'],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.1,
        "max_tokens": 200,
        "stream": False
    }
    response = requests.post(
        f"{settings.AI_MODELS['DEEPSEEK']['BASE_URL']}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.AI_MODELS['DEEPSEEK']['API_KEY']}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    raw_content = data["choices"][0]["message"]["content"]
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as e:
        return {
            "error": "Invalid JSON content returned by the AI service.",
            "details": str(e),
            "raw_content": raw_content
        } 