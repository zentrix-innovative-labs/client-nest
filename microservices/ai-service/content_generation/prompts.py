# microservices/ai-service/content_generation/prompts.py

"""
Token-optimized prompt templates for AI content generation.
Optimized for 1M token budget with concise prompts.
"""

def get_base_system_prompt(platform, tone, language="English"):
    """
    Creates a token-efficient base system prompt for the AI model.
    """
    platform_instructions = {
        'twitter': 'Keep under 280 chars. Use hashtags.',
        'instagram': 'Visual hook. Use hashtags and emojis.',
        'linkedin': 'Professional tone. Industry insights.',
        'facebook': 'Community interaction. Friendly tone.'
    }

    tone_instructions = {
        'professional': 'Formal, industry terms.',
        'casual': 'Conversational, emojis ok.',
        'witty': 'Humor, clever wordplay.',
        'inspirational': 'Uplifting, motivational.'
    }

    return f"""Create {platform} content in {language}. Tone: {tone}. Guidelines: {platform_instructions.get(platform, 'Engaging content.')} Tone: {tone_instructions.get(tone, 'Neutral tone.')}

Return JSON: content, hashtags (array), call_to_action, suggestions (array), variations (array), quality_score (1-100), safety_check (is_safe boolean, reason string), readability_score (number)."""

def get_user_prompt(topic, content_type="post", additional_context=None):
    """
    Creates a token-efficient user-facing prompt.
    """
    context_str = f" Context: {additional_context}" if additional_context else ""
    return f"Topic: {topic}. Type: {content_type}.{context_str} Generate content." 