# ai_services/content_generation/logic.py
import json
from typing import Dict, Any

from ai_services.common.deepseek_client import DeepSeekClient, AIClientError
from ai_services.common.utils import truncate_text, calculate_readability_score
from ai_services.content_generation.prompts import get_base_system_prompt, get_user_prompt
from django.conf import settings

class ContentGenerator:
    """
    Handles all logic related to content generation, enhancement, and optimization.
    This version is synchronous and uses the robust, production-ready DeepSeekClient.
    """
    PLATFORM_CONFIGS = {
        'twitter': {'max_length': 280},
        'instagram': {'max_length': 2200},
        'linkedin': {'max_length': 3000},
        'facebook': {'max_length': 63206}
    }

    def __init__(self, deepseek_client: DeepSeekClient):
        self.client = deepseek_client

    def generate_post(self, topic: str, platform: str, user: Any, tone: str = 'professional', 
                            content_type: str = 'post', additional_context: str = None) -> Dict[str, Any]:
        """
        Main method for generating a complete, platform-aware social media post.
        """
        system_prompt = get_base_system_prompt(platform, tone)
        user_prompt = get_user_prompt(topic, content_type, additional_context)
        
        try:
            response_data = self.client.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                user=user
            )
        except AIClientError as e:
            # Catch client-specific errors and return a structured error response
            return {"error": str(e)}

        return self._process_and_enhance_response(response_data, platform)

    def _process_and_enhance_response(self, response_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Processes the raw AI response and applies platform-specific rules and enhancements.
        (Sprint 2, Week 1 & 2: Platform-specific optimization, content enhancement)
        """
        # If response_data is a string, try to parse as JSON
        if isinstance(response_data, str):
            try:
                response_data = json.loads(response_data)
            except Exception:
                return {"error": "Failed to decode AI response as JSON.", "raw_response": response_data}
        # If not a dict after parsing, return error
        if not isinstance(response_data, dict):
            return {"error": "AI response is not a dictionary.", "raw_response": response_data}

        config = self.PLATFORM_CONFIGS.get(platform, {})
        max_length = config.get('max_length')

        # Optimize content length for the platform
        if max_length and 'content' in response_data:
            original_content = response_data['content']
            response_data['content'] = truncate_text(original_content, max_length)
            if len(original_content) > max_length:
                response_data.setdefault('suggestions', []).append(f"Content was truncated to {max_length} characters for {platform}.")
        
        # Calculate readability if not already provided by the AI
        if 'readability_score' not in response_data and 'content' in response_data:
            response_data['readability_score'] = calculate_readability_score(response_data['content'])

        # (Sprint 2, Week 3: Engagement Optimization & Quality Control - Simplified)
        # In a real scenario, these would be more complex models.
        # Only set these if the AI hasn't already provided them.
        if 'engagement_prediction' not in response_data:
            response_data['engagement_prediction'] = self._predict_engagement(response_data)
        if 'optimal_posting_time_suggestion' not in response_data:
            response_data['optimal_posting_time_suggestion'] = self._suggest_posting_time(platform)

        return response_data

    def _predict_engagement(self, response_data: Dict[str, Any]) -> str:
        """
        Simplified engagement prediction based on content quality and features.
        (Sprint 2, Week 3)
        """
        score = response_data.get('quality_score', 0)
        has_cta = bool(response_data.get('call_to_action'))
        has_hashtags = bool(response_data.get('hashtags'))

        if score > 85 and has_cta and has_hashtags:
            return "High"
        if score > 60 and (has_cta or has_hashtags):
            return "Medium"
        return "Low"

    def _suggest_posting_time(self, platform: str) -> str:
        """
        Simplified posting time suggestion.
        (Sprint 2, Week 3)
        """
        times = {
            'twitter': '8-10 AM on weekdays',
            'instagram': '11 AM - 2 PM on weekdays',
            'linkedin': '9 AM - 11 AM on Tue, Wed, Thu',
            'facebook': '1 PM - 3 PM on weekdays'
        }
        return times.get(platform, "Check your audience analytics for the best time.")

# The async main function is no longer needed for direct testing,
# as the class is now synchronous. 