from ai_services.common.deepseek_client import DeepSeekClient
from typing import Dict, Any

class Optimizer:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def optimize(self, content: str, platform: str, optimization_type: str = 'engagement') -> Dict[str, Any]:
        async with DeepSeekClient(self.api_key) as client:
            result = await client.optimize_content(
                content=content,
                platform=platform,
                optimization_type=optimization_type
            )
            return result 