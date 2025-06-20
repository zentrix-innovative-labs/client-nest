import unittest
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ai_services.optimization.logic import Optimizer

class TestOptimizer(unittest.IsolatedAsyncioTestCase):
    @patch('ai_services.optimization.logic.DeepSeekClient')
    async def test_optimize(self, MockDeepSeekClient):
        mock_client = MockDeepSeekClient.return_value.__aenter__.return_value
        mock_client.optimize_content = AsyncMock(return_value={'optimized_content': 'better content'})
        optimizer = Optimizer(api_key='fake-key')
        result = await optimizer.optimize('content', platform='twitter', optimization_type='engagement')
        self.assertEqual(result, {'optimized_content': 'better content'})
        mock_client.optimize_content.assert_awaited_once_with(content='content', platform='twitter', optimization_type='engagement')

if __name__ == '__main__':
    unittest.main() 