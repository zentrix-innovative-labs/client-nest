import unittest
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ai_services.sentiment_analysis.logic import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.IsolatedAsyncioTestCase):
    @patch('ai_services.sentiment_analysis.logic.DeepSeekClient')
    async def test_analyze(self, MockDeepSeekClient):
        mock_client = MockDeepSeekClient.return_value.__aenter__.return_value
        mock_client.analyze_sentiment = AsyncMock(return_value={'sentiment': 'positive'})
        analyzer = SentimentAnalyzer(api_key='fake-key')
        result = await analyzer.analyze('text', context='comment')
        self.assertEqual(result, {'sentiment': 'positive'})
        mock_client.analyze_sentiment.assert_awaited_once_with(text='text', context='comment')

if __name__ == '__main__':
    unittest.main() 