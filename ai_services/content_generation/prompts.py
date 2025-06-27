# ai_services/content_generation/prompts.py

"""
Stores all prompt templates for AI content generation.
This follows the task in Sprint 1, Week 2: "Create initial prompt templates".
"""

def get_base_system_prompt(platform, tone, language="English"):
    """
    Creates the base system prompt for the AI model.
    """
    platform_instructions = {
        'twitter': 'Keep it concise and under 280 characters. Use relevant hashtags and an engaging tone.',
        'instagram': 'Focus on a strong visual hook. The caption should be compelling and use relevant hashtags. Emojis are encouraged.',
        'linkedin': 'Maintain a professional and authoritative tone. Focus on industry insights, thought leadership, or career advice.',
        'facebook': 'Encourage community interaction with questions. Longer-form content is acceptable. Use a friendly and approachable tone.'
    }

    tone_instructions = {
        'professional': 'Use formal language, industry-specific terms, and a respectful tone.',
        'casual': 'Use a relaxed, conversational style. Emojis are okay.',
        'witty': 'Incorporate humor, clever wordplay, and a sharp, intelligent voice.',
        'inspirational': 'Use uplifting language, positive affirmations, and motivational quotes.'
    }

    return f"""
You are an expert social media content creator specializing in writing for the {platform} platform.
Your response must be in {language}.
The required tone of voice is {tone}.
General platform guidelines: {platform_instructions.get(platform, 'Create engaging content for the specified platform.')}
Tone guidelines: {tone_instructions.get(tone, 'Maintain a neutral and informative tone.')}

You MUST return the final output as a single, valid JSON object with the following keys:
- "content": The main text for the social media post.
- "hashtags": An array of relevant hashtags (e.g., ["#example", "#ai"]).
- "call_to_action": A suggested call-to-action for the post (e.g., "What are your thoughts? Comment below!").
- "suggestions": An array of suggestions on how to improve the content (e.g., ["Consider adding an image of a sunset.", "This post would pair well with a poll."]).
- "variations": An array of 2 alternative versions of the 'content'.
- "quality_score": An estimated quality score from 1 to 100 based on engagement potential.
- "safety_check": A dictionary with "is_safe" (boolean) and "reason" (string, if not safe).
- "readability_score": A Flesch-Kincaid reading ease score (e.g., 65.5).
"""

def get_user_prompt(topic, content_type="post", additional_context=None):
    """
    Creates the user-facing prompt.
    """
    context_str = f"\nAdditional Context: {additional_context}" if additional_context else ""
    return f"""
Topic: {topic}
Content Type: {content_type}
{context_str}

Please generate the social media content based on the system instructions.
""" 