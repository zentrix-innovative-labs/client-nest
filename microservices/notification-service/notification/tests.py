from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class NotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_create_notification(self):
        url = reverse('notification-list-create')
        data = {'message': 'Test notification', 'notification_type': 'info', 'user': self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)

    def test_list_notifications(self):
        Notification.objects.create(user=self.user, message='Test', notification_type='info')
        url = reverse('notification-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
