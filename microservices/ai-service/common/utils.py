"""
Common utility functions for the AI services.
"""
import re

def truncate_text(text: str, max_length: int) -> str:
    """
    Truncates text to a maximum length without cutting words.
    """
    if len(text) <= max_length:
        return text
    # Find the last space before max_length - 3 to avoid breaking words
    last_space = text.rfind(' ', 0, max_length - 3)
    if last_space == -1:
        return text[:max_length - 3] + '...'
    return text[:last_space] + '...'

def calculate_readability_score(text):
    """
    Calculates the Flesch-Kincaid reading ease score.
    A higher score means easier to read.
    This is a simplified implementation.
    """
    # Convert text to lowercase once before processing
    text_lower = text.lower()
    words = text_lower.split()
    num_words = len(words)
    
    # Improved sentence counting using regex to better handle various sentence endings.
    sentences = re.split(r'[.!?]+', text)
    # Filter out empty strings that may result from the split
    num_sentences = len([s for s in sentences if s.strip()])
    
    num_syllables = 0
    
    if num_words == 0:
        return 0.0
    
    # Ensure num_sentences is at least 1 to avoid division by zero.
    if num_sentences == 0:
        num_sentences = 1

    for word in words:
        # A very basic syllable counter
        syllable_count = len(re.findall(r'[aeiouy]+', word))
        if word.endswith('e'):
            syllable_count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
            syllable_count += 1
        if syllable_count == 0:
            syllable_count = 1
        num_syllables += syllable_count

    try:
        score = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words)
        return round(score, 2)
    except ZeroDivisionError:
        return 0.0 

def calculate_token_usage_cost(usage_data, settings, pricing_key='prompt'):
    """
    Calculate the number of tokens consumed and the cost based on usage data and settings.
    Args:
        usage_data (dict): Usage data from the AI client (should include prompt_tokens, completion_tokens, or total_tokens).
        settings (module): Django settings module (should include DEFAULT_TOKEN_FALLBACK and DEEPSEEK_PRICING).
        pricing_key (str): The pricing key to use from DEEPSEEK_PRICING (default: 'prompt').
    Returns:
        tuple: (tokens_consumed, cost)
    """
    prompt_tokens = usage_data.get('prompt_tokens', 0)
    completion_tokens = usage_data.get('completion_tokens', 0)
    if prompt_tokens or completion_tokens:
        tokens_consumed = prompt_tokens + completion_tokens
    else:
        tokens_consumed = usage_data.get('total_tokens') or getattr(settings, 'DEFAULT_TOKEN_FALLBACK', 234)
    cost_per_1k = getattr(settings, 'DEEPSEEK_PRICING', {}).get(pricing_key, 0.001)
    cost = (tokens_consumed / 1000) * cost_per_1k
    return tokens_consumed, round(cost, 4) 