from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import AIModel, AITask

User = get_user_model()

class AIModelTests(TestCase):
    """Test cases for AIModel"""

    def setUp(self):
        self.model_data = {
            'name': 'Test Model',
            'description': 'Test Description',
            'version': '1.0'
        }
        self.model = AIModel.objects.create(**self.model_data)

    def test_model_creation(self):
        """Test AIModel creation"""
        self.assertEqual(self.model.name, self.model_data['name'])
        self.assertEqual(self.model.description, self.model_data['description'])
        self.assertEqual(self.model.version, self.model_data['version'])
        self.assertIsNotNone(self.model.created_at)
        self.assertIsNotNone(self.model.updated_at)

    def test_model_str_representation(self):
        """Test AIModel string representation"""
        expected_str = f"{self.model_data['name']} v{self.model_data['version']}"
        self.assertEqual(str(self.model), expected_str)

    def test_model_update(self):
        """Test AIModel update"""
        new_version = '2.0'
        old_updated_at = self.model.updated_at

        # Wait a moment to ensure updated_at will be different
        import time
        time.sleep(0.1)

        self.model.version = new_version
        self.model.save()

        # Refresh from database
        self.model.refresh_from_db()

        self.assertEqual(self.model.version, new_version)
        self.assertGreater(self.model.updated_at, old_updated_at)

class AITaskTests(TestCase):
    """Test cases for AITask"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test model
        self.model = AIModel.objects.create(
            name='Test Model',
            description='Test Description',
            version='1.0'
        )

        # Create test task
        self.task_data = {
            'model': self.model,
            'user': self.user,
            'input_data': {'type': 'test', 'prompt': 'test prompt'},
            'status': 'pending'
        }
        self.task = AITask.objects.create(**self.task_data)

    def test_task_creation(self):
        """Test AITask creation"""
        self.assertEqual(self.task.model, self.task_data['model'])
        self.assertEqual(self.task.user, self.task_data['user'])
        self.assertEqual(self.task.input_data, self.task_data['input_data'])
        self.assertEqual(self.task.status, self.task_data['status'])
        self.assertIsNone(self.task.output_data)
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)

    def test_task_str_representation(self):
        """Test AITask string representation"""
        expected_str = f"{self.model.name} task for {self.user.username} at {self.task.created_at}"
        self.assertEqual(str(self.task), expected_str)

    def test_task_status_update(self):
        """Test AITask status update"""
        new_status = 'completed'
        output_data = {'result': 'test result'}
        old_updated_at = self.task.updated_at

        # Wait a moment to ensure updated_at will be different
        import time
        time.sleep(0.1)

        self.task.status = new_status
        self.task.output_data = output_data
        self.task.save()

        # Refresh from database
        self.task.refresh_from_db()

        self.assertEqual(self.task.status, new_status)
        self.assertEqual(self.task.output_data, output_data)
        self.assertGreater(self.task.updated_at, old_updated_at)

    def test_task_status_choices(self):
        """Test AITask status choices"""
        valid_statuses = ['pending', 'processing', 'completed', 'failed']

        for status in valid_statuses:
            self.task.status = status
            self.task.save()
            self.assertEqual(self.task.status, status)

    def test_task_with_large_data(self):
        """Test AITask with large input/output data"""
        large_input_data = {
            'type': 'test',
            'prompt': 'x' * 1000,  # Large prompt
            'parameters': {
                'key1': 'x' * 100,
                'key2': 'x' * 100,
            }
        }
        large_output_data = {
            'result': 'x' * 1000,
            'metadata': {
                'key1': 'x' * 100,
                'key2': 'x' * 100,
            }
        }

        self.task.input_data = large_input_data
        self.task.output_data = large_output_data
        self.task.save()

        # Refresh from database
        self.task.refresh_from_db()

        self.assertEqual(self.task.input_data, large_input_data)
        self.assertEqual(self.task.output_data, large_output_data)