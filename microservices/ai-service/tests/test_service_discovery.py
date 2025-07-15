import unittest
from unittest.mock import patch
import os

from common.service_discovery import ServiceDiscovery

class TestServiceDiscovery(unittest.TestCase):
    def setUp(self):
        # Reset the registry before each test
        ServiceDiscovery._registry = {}

    def test_register_and_discover_service(self):
        ServiceDiscovery.register_service('ai-service', 'localhost', 8005)
        services = ServiceDiscovery.discover_services()
        self.assertIn('ai-service', services)
        self.assertEqual(services['ai-service']['host'], 'localhost')
        self.assertEqual(services['ai-service']['port'], 8005)

    def test_duplicate_registration_overwrites(self):
        ServiceDiscovery.register_service('ai-service', 'localhost', 8005)
        ServiceDiscovery.register_service('ai-service', '127.0.0.1', 9000)
        services = ServiceDiscovery.discover_services()
        self.assertEqual(services['ai-service']['host'], '127.0.0.1')
        self.assertEqual(services['ai-service']['port'], 9000)

    def test_health_check_success(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            result = ServiceDiscovery.health_check('localhost', 8005)
            self.assertTrue(result)
            mock_get.assert_called_once()

    def test_health_check_failure(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception('Connection error')
            result = ServiceDiscovery.health_check('localhost', 8005)
            self.assertFalse(result)

    def test_discover_services_empty(self):
        services = ServiceDiscovery.discover_services()
        self.assertEqual(services, {})

if __name__ == '__main__':
    unittest.main() 