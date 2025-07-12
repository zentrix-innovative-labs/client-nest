# microservices/ai-service/content_generation/prompts.py

"""
Prompt templates for AI content generation
Extracted from views for better maintainability and reusability
"""

def generate_hashtag_optimization_prompt(content: str, platform: str, target_audience: str, industry: str) -> str:
    """
    Generate hashtag optimization prompt
    
    Args:
        content: The content to optimize hashtags for
        platform: Social media platform (linkedin, twitter, instagram, facebook)
        target_audience: Target audience for the content
        industry: Industry context
    
    Returns:
        Formatted prompt string
    """
    return f"""
Analyze the following content and suggest optimal hashtags for {platform} platform.

Content: {content}
Platform: {platform}
Target Audience: {target_audience}
Industry: {industry}

Please provide:
1. 5-10 relevant hashtags with high engagement potential
2. Mix of popular and niche hashtags
3. Platform-specific hashtag strategies
4. Estimated reach for each hashtag category

IMPORTANT: Return ONLY valid JSON without any markdown formatting or code blocks.

{{
    "hashtags": [
        {{
            "tag": "hashtag",
            "category": "popular|niche|trending",
            "estimated_reach": "high|medium|low",
            "engagement_potential": "high|medium|low"
        }}
    ],
    "strategy": {{
        "platform_specific": "string",
        "audience_targeting": "string",
        "trending_opportunities": "string"
    }},
    "recommendations": [
        "string"
    ]
}}
"""

def generate_optimal_posting_time_prompt(platform: str, content_type: str, target_audience: str, 
                                       timezone: str, industry: str) -> str:
    """
    Generate optimal posting time prompt
    
    Args:
        platform: Social media platform
        content_type: Type of content (post, story, video, etc.)
        target_audience: Target audience
        timezone: User's timezone
        industry: Industry context
    
    Returns:
        Formatted prompt string
    """
    return f"""
Analyze and suggest optimal posting times for {platform} platform.

Platform: {platform}
Content Type: {content_type}
Target Audience: {target_audience}
Timezone: {timezone}
Industry: {industry}

Please provide:
1. Best posting times for different days of the week
2. Platform-specific timing strategies
3. Audience behavior patterns
4. Industry-specific timing recommendations

IMPORTANT: Return ONLY valid JSON without any markdown formatting or code blocks.

{{
    "optimal_times": {{
        "monday": ["09:00", "12:00", "18:00"],
        "tuesday": ["09:00", "12:00", "18:00"],
        "wednesday": ["09:00", "12:00", "18:00"],
        "thursday": ["09:00", "12:00", "18:00"],
        "friday": ["09:00", "12:00", "18:00"],
        "saturday": ["10:00", "14:00", "19:00"],
        "sunday": ["10:00", "14:00", "19:00"]
    }},
    "platform_strategy": {{
        "best_days": ["monday", "wednesday", "friday"],
        "best_hours": ["09:00-11:00", "12:00-14:00", "18:00-20:00"],
        "audience_peak_times": "string",
        "engagement_patterns": "string"
    }},
    "recommendations": [
        "string"
    ],
    "timezone_considerations": "string"
}}
"""

def generate_content_generation_prompt(topic: str, platform: str, tone: str, content_type: str = "post") -> str:
    """
    Generate content generation prompt
    
    Args:
        topic: Content topic
        platform: Social media platform
        tone: Content tone (professional, casual, etc.)
        content_type: Type of content
    
    Returns:
        Formatted prompt string
    """
    return f"""
Create engaging {content_type} content for {platform} about "{topic}" with a {tone} tone.

Requirements:
1. Engaging and platform-appropriate content
2. Relevant hashtags for maximum reach
3. Clear call-to-action
4. Optimized for {platform} audience
5. {tone.title()} tone throughout

Format the response as JSON with the following structure:
{{
    "content": "main content text",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "call_to_action": "clear call to action",
    "quality_score": 85,
    "safety_check": {{"safe": true, "warnings": []}},
    "readability_score": 8.5,
    "engagement_prediction": "high",
    "optimal_posting_time_suggestion": "Best time to post"
}}
"""

def get_base_system_prompt(platform: str, tone: str, language: str = "English") -> str:
    """
    Creates a token-efficient base system prompt for the AI model.
    
    Args:
        platform: Social media platform
        tone: Content tone
        language: Language for content generation
    
    Returns:
        System prompt string
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

def get_user_prompt(topic: str, content_type: str = "post", additional_context: str = None) -> str:
    """
    Creates a token-efficient user-facing prompt.
    
    Args:
        topic: Content topic
        content_type: Type of content
        additional_context: Additional context for content generation
    
    Returns:
        User prompt string
    """
    context_str = f" Context: {additional_context}" if additional_context else ""
    return f"Topic: {topic}. Type: {content_type}.{context_str} Generate content." 