from ai_services.common.deepseek_client import DeepSeekClient
from typing import Dict, Any

class SentimentAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def analyze(self, text: str, context: str = 'comment') -> Dict[str, Any]:
        async with DeepSeekClient(self.api_key) as client:
            result = await client.analyze_sentiment(
                text=text,
                context=context
            )
            return result 