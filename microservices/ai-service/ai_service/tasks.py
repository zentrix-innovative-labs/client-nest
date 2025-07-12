from celery import shared_task
from django.conf import settings
import requests
import json

@shared_task
def generate_content_task(topic, platform='general', tone='professional'):
    system_prompt = f"You are an expert social media content creator for {platform}. Use a {tone} tone. Return a JSON object with keys: content, hashtags, call_to_action, suggestions, variations, quality_score, safety_check, readability_score."
    user_prompt = f"Topic: {topic}\nGenerate a post."
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
    return json.loads(raw_content)

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
    return json.loads(raw_content) 