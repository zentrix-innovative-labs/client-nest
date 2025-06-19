from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import AIModel, AITask
from ..serializers import (
    AIModelSerializer,
    AITaskSerializer,
    ContentGenerationSerializer,
    SentimentAnalysisSerializer
)

User = get_user_model()

class AISerializerTests(TestCase):
    """Test cases for AI integration serializers"""

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
        self.task = AITask.objects.create(
            model=self.model,
            user=self.user,
            input_data={'type': 'test', 'prompt': 'test prompt'},
            output_data={'result': 'test output'},
            status='completed'
        )

    def test_ai_model_serializer(self):
        """Test AIModelSerializer"""
        serializer = AIModelSerializer(self.model)
        data = serializer.data

        self.assertEqual(data['name'], self.model.name)
        self.assertEqual(data['description'], self.model.description)
        self.assertEqual(data['version'], self.model.version)

        # Test validation
        invalid_data = {
            'name': '',  # Empty name
            'description': 'Test',
            'version': '1.0'
        }
        serializer = AIModelSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_ai_task_serializer(self):
        """Test AITaskSerializer"""
        serializer = AITaskSerializer(self.task)
        data = serializer.data

        self.assertEqual(data['model']['name'], self.model.name)
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['input_data']['type'], 'test')
        self.assertEqual(data['output_data']['result'], 'test output')

        # Test validation
        invalid_data = {
            'model': self.model.id,
            'user': self.user.id,
            'input_data': None,  # Invalid input data
            'status': 'invalid'  # Invalid status
        }
        serializer = AITaskSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('input_data', serializer.errors)
        self.assertIn('status', serializer.errors)

    def test_content_generation_serializer(self):
        """Test ContentGenerationSerializer"""
        valid_data = {
            'prompt': 'Test prompt',
            'platform': 'twitter',
            'tone': 'professional',
            'language': 'en',
            'keywords': ['test', 'ai']
        }
        serializer = ContentGenerationSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Test prompt validation
        invalid_data = valid_data.copy()
        invalid_data['prompt'] = ''  # Empty prompt
        serializer = ContentGenerationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('prompt', serializer.errors)

        # Test platform validation
        invalid_data = valid_data.copy()
        invalid_data['platform'] = 'invalid'  # Invalid platform
        serializer = ContentGenerationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('platform', serializer.errors)

        # Test keywords validation
        invalid_data = valid_data.copy()
        invalid_data['keywords'] = ['test'] * 11  # Too many keywords
        serializer = ContentGenerationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('keywords', serializer.errors)

    def test_sentiment_analysis_serializer(self):
        """Test SentimentAnalysisSerializer"""
        valid_data = {
            'text': 'Great product! Really satisfied with the quality.',
            'language': 'en',
            'context': 'review'
        }
        serializer = SentimentAnalysisSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Test text validation
        invalid_data = valid_data.copy()
        invalid_data['text'] = ''  # Empty text
        serializer = SentimentAnalysisSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('text', serializer.errors)

        # Test text length validation
        invalid_data = valid_data.copy()
        invalid_data['text'] = 'x' * 5001  # Text too long
        serializer = SentimentAnalysisSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('text', serializer.errors)

        # Test context validation
        invalid_data = valid_data.copy()
        invalid_data['context'] = 'invalid'  # Invalid context
        serializer = SentimentAnalysisSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('context', serializer.errors)

    def test_serializer_field_types(self):
        """Test serializer field types and formats"""
        # Test AIModelSerializer fields
        model_serializer = AIModelSerializer()
        self.assertEqual(model_serializer.fields['name'].required, True)
        self.assertEqual(model_serializer.fields['version'].required, True)

        # Test AITaskSerializer fields
        task_serializer = AITaskSerializer()
        self.assertEqual(task_serializer.fields['model'].required, True)
        self.assertEqual(task_serializer.fields['status'].required, True)

        # Test ContentGenerationSerializer fields
        content_serializer = ContentGenerationSerializer()
        self.assertEqual(content_serializer.fields['prompt'].required, True)
        self.assertEqual(content_serializer.fields['platform'].required, True)
        self.assertEqual(content_serializer.fields['keywords'].required, False)

        # Test SentimentAnalysisSerializer fields
        sentiment_serializer = SentimentAnalysisSerializer()
        self.assertEqual(sentiment_serializer.fields['text'].required, True)
        self.assertEqual(sentiment_serializer.fields['language'].required, True)
        self.assertEqual(sentiment_serializer.fields['context'].required, True)