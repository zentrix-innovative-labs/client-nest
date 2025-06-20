from ai_services.common.deepseek_client import DeepSeekClient
from typing import Dict, Any

class ContentGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate_post(self, prompt: str, platform: str = 'general', content_type: str = 'post', **kwargs) -> Dict[str, Any]:
        async with DeepSeekClient(self.api_key) as client:
            result = await client.generate_content(
                prompt=prompt,
                content_type=content_type,
                platform=platform,
                **kwargs
            )
            return result 