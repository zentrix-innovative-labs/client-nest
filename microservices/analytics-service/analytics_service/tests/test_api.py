from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

class AnalyticsAPITests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_dashboard_endpoint_requires_auth(self):
        self.client.logout()
        url = reverse('analytics-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_engagement_prediction(self):
        url = reverse('analytics-engagement')
        # Example features for provisional model (length 3)
        data = {'features': [0.5, 0.2, 0.8]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prediction', response.data)
        self.assertIsInstance(response.data['prediction'], float)

    def test_insights_endpoint(self):
        url = reverse('analytics-insights')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('insights', response.data)
        self.assertIsInstance(response.data['insights'], list)
        self.assertGreater(len(response.data['insights']), 0) 