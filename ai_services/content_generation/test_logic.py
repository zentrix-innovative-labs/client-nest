# ai_services/content_generation/test_logic.py
import json
import pytest
from unittest.mock import AsyncMock

from ai_services.content_generation.logic import ContentGenerator
from ai_services.common.deepseek_client import DeepSeekClient

# A sample successful response from the AI, structured as a JSON string
SAMPLE_SUCCESS_RESPONSE = json.dumps({
    "content": "This is a brilliantly generated post about AI in business.",
    "hashtags": ["#AI", "#Business", "#Innovation"],
    "call_to_action": "What are your thoughts on AI?",
    "suggestions": [],
    "variations": [
        {"content": "Discover how AI is transforming the business landscape.", "tone": "Informative"},
        {"content": "Is your business leveraging AI? Here's why you should start.", "tone": "Persuasive"}
    ],
    "quality_score": 95,
    "safety_check": {"is_safe": True, "reason": "N/A"},
    "readability_score": 70.2,
    "engagement_prediction": "High",
    "optimal_posting_time_suggestion": "10 AM on weekdays"
})

@pytest.fixture
def mock_deepseek_client():
    """Fixture to create a mock DeepSeekClient that can be used as an async context manager."""
    mock_client = AsyncMock(spec=DeepSeekClient)
    # The __aenter__ must return an awaitable that resolves to the mock client instance.
    mock_client.__aenter__.return_value = mock_client
    return mock_client

class TestContentGenerator:
    """Unit tests for the ContentGenerator logic, using a mocked client."""

    def test_generate_post_success(self, mock_deepseek_client):
        """Tests a successful content generation call."""
        # Arrange: Configure the mock to return a successful response
        mock_deepseek_client.generate_content.return_value = SAMPLE_SUCCESS_RESPONSE
        generator = ContentGenerator(mock_deepseek_client)
        user = {"id": 1, "name": "Test User"}
        result = generator.generate_post(
            topic="AI for small business marketing",
            platform="linkedin",
            tone="professional",
            user=user
        )
        
        # Assert: Check that the result is correctly parsed and structured
        assert result['content'] == "This is a brilliantly generated post about AI in business."
        assert "#AI" in result['hashtags']
        assert result['quality_score'] == 95
        assert result['safety_check']['is_safe'] is True
        assert len(result['variations']) == 2
        mock_deepseek_client.generate_content.assert_called_once()

    def test_twitter_length_truncation(self, mock_deepseek_client):
        """Tests that content for Twitter is correctly truncated if it exceeds the character limit."""
        # Arrange: Create a response with content that is too long for Twitter
        long_content = "This is an extremely long post that definitely exceeds the 280 character limit for Twitter, designed to test the truncation logic and ensure that posts remain compliant with platform constraints." * 5
        response_data = json.loads(SAMPLE_SUCCESS_RESPONSE)
        response_data['content'] = long_content
        mock_deepseek_client.generate_content.return_value = json.dumps(response_data)
        generator = ContentGenerator(mock_deepseek_client)
        user = {"id": 1, "name": "Test User"}
        result = generator.generate_post(topic="Long topic", platform="twitter", tone="casual", user=user)
        
        # Assert
        assert len(result['content']) <= 280
        assert 'Content was truncated to 280 characters for twitter.' in result.get('suggestions', [])

    def test_json_parsing_error(self, mock_deepseek_client):
        """Tests handling of a non-JSON response from the AI."""
        # Arrange: Configure the mock to return a malformed string
        raw_response = "This is not valid JSON."
        mock_deepseek_client.generate_content.return_value = raw_response
        generator = ContentGenerator(mock_deepseek_client)
        user = {"id": 1, "name": "Test User"}
        result = generator.generate_post(topic="Test error", platform="linkedin", tone="professional", user=user)
        
        # Assert: Check that the error is handled gracefully
        assert 'error' in result
        assert "Failed to decode AI response" in result['error']
        assert result['raw_response'] == raw_response

@pytest.mark.asyncio
async def test_generate_post_safety_check():
    generator = ContentGenerator(DeepSeekClient())
    result = generator.generate_post(
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
    result = generator.generate_post(
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
    result = generator.generate_post(
        topic="Test error handling",
        platform="linkedin",
        tone="professional"
    )
    assert 'error' in result
    assert 'raw_response' in result 