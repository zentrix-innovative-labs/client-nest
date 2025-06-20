import aiohttp
import json
from typing import Dict, Any
from .utils import RateLimiter, CircuitBreaker

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = 'https://api.deepseek.com/v1'):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'ClientNest/1.0'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def generate_content(self, prompt: str, content_type: str = 'post', platform: str = 'general', **kwargs) -> Dict[str, Any]:
        if not await self.rate_limiter.acquire():
            raise Exception('Rate limit exceeded')
        if not self.circuit_breaker.can_execute():
            raise Exception('Service temporarily unavailable')
        payload = self._build_content_payload(prompt, content_type, platform, **kwargs)
        try:
            async with self.session.post(f'{self.base_url}/chat/completions', json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    self.circuit_breaker.record_success()
                    return result
                else:
                    self.circuit_breaker.record_failure()
                    raise Exception(f'DeepSeek API error: {response.status}')
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise

    async def analyze_sentiment(self, text: str, context: str = 'comment') -> Dict[str, Any]:
        if not await self.rate_limiter.acquire():
            raise Exception('Rate limit exceeded')
        if not self.circuit_breaker.can_execute():
            raise Exception('Service temporarily unavailable')
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': f'You are a sentiment analysis expert. Analyze the sentiment of the given {context}.'},
                {'role': 'user', 'content': text}
            ],
            'temperature': 0.1,
            'max_tokens': 200
        }
        try:
            async with self.session.post(f'{self.base_url}/chat/completions', json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    self.circuit_breaker.record_success()
                    return result
                else:
                    self.circuit_breaker.record_failure()
                    raise Exception(f'Sentiment analysis failed: {response.status}')
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise

    def _build_content_payload(self, prompt: str, content_type: str, platform: str, **kwargs) -> Dict[str, Any]:
        system_prompt = f'You are an expert social media content creator. Create a {content_type} for {platform}.'
        return {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': kwargs.get('temperature', 0.8),
            'max_tokens': kwargs.get('max_tokens', 800),
            'top_p': kwargs.get('top_p', 0.9)
        } 