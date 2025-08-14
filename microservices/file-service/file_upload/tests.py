from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

class FileUploadTests(APITestCase):
    def test_file_upload(self):
        url = reverse('file-upload')
        file_data = SimpleUploadedFile('test.txt', b'hello world', content_type='text/plain')
        data = {'file': file_data, 'description': 'Test file'}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file', response.data)
