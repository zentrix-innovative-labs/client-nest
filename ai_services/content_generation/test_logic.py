# ai_services/content_generation/test_logic.py
import asyncio
import json
import pytest

from ai_services.content_generation.logic import ContentGenerator
from ai_services.common.deepseek_client import DeepSeekClient

@pytest.mark.asyncio
async def test_generate_post_basic():
    generator = ContentGenerator(DeepSeekClient())
    result = await generator.generate_post(
        topic="AI for small business marketing",
        platform="linkedin",
        tone="professional"
    )
    assert 'content' in result
    assert 'hashtags' in result
    assert isinstance(result['hashtags'], list)
    assert 'call_to_action' in result
    assert 'quality_score' in result
    assert 'readability_score' in result
    assert 'engagement_prediction' in result
    assert 'optimal_posting_time_suggestion' in result
    assert result['content']
    assert result['quality_score'] >= 0
    assert result['readability_score'] >= 0

@pytest.mark.asyncio
async def test_generate_post_twitter_length():
    generator = ContentGenerator(DeepSeekClient())
    result = await generator.generate_post(
        topic="A very long topic that will likely exceed the Twitter character limit and should be truncated accordingly to fit the platform's requirements.",
        platform="twitter",
        tone="casual"
    )
    assert len(result['content']) <= 280
    assert 'Content was truncated to 280 characters for twitter.' in result.get('suggestions', []) or len(result['content']) < 280

@pytest.mark.asyncio
async def test_generate_post_safety_check():
    generator = ContentGenerator(DeepSeekClient())
    result = await generator.generate_post(
        topic="Sensitive topic",
        platform="facebook",
        tone="inspirational"
    )
    assert 'safety_check' in result
    assert isinstance(result['safety_check'], dict)
    assert 'is_safe' in result['safety_check']

@pytest.mark.asyncio
async def test_generate_post_variations():
    generator = ContentGenerator(DeepSeekClient())
    result = await generator.generate_post(
        topic="Remote work tips",
        platform="instagram",
        tone="witty"
    )
    assert 'variations' in result
    assert isinstance(result['variations'], list)
    assert len(result['variations']) == 2

@pytest.mark.asyncio
async def test_generate_post_error_handling():
    class BadClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def generate_content(self, system_prompt, user_prompt, **kwargs):
            return "not a json string"
    generator = ContentGenerator(BadClient())
    result = await generator.generate_post(
        topic="Test error handling",
        platform="linkedin",
        tone="professional"
    )
    assert 'error' in result
    assert 'raw_response' in result 