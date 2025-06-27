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
    words = text.split()
    num_words = len(words)
    num_sentences = text.count('.') + text.count('!') + text.count('?')
    num_syllables = 0
    
    if num_words == 0 or num_sentences == 0:
        return 0.0

    for word in words:
        # A very basic syllable counter
        word = word.lower()
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