import unittest
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ai_services.content_generation.logic import ContentGenerator

class TestContentGenerator(unittest.IsolatedAsyncioTestCase):
    @patch('ai_services.content_generation.logic.DeepSeekClient')
    async def test_generate_post(self, MockDeepSeekClient):
        mock_client = MockDeepSeekClient.return_value.__aenter__.return_value
        mock_client.generate_content = AsyncMock(return_value={'content': 'test result'})
        generator = ContentGenerator(api_key='fake-key')
        result = await generator.generate_post('prompt', platform='twitter', content_type='post')
        self.assertEqual(result, {'content': 'test result'})
        mock_client.generate_content.assert_awaited_once_with(prompt='prompt', content_type='post', platform='twitter')

if __name__ == '__main__':
    unittest.main() 