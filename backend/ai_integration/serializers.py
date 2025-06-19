from rest_framework import serializers
from .models import AITask, AIModel

class AIModelSerializer(serializers.ModelSerializer):
    """Serializer for AI models"""
    class Meta:
        model = AIModel
        fields = ['id', 'name', 'description', 'version', 'created_at', 'updated_at']
        read_only_fields = fields

class AITaskSerializer(serializers.ModelSerializer):
    """Serializer for AI tasks"""
    model = AIModelSerializer(read_only=True)

    class Meta:
        model = AITask
        fields = ['id', 'model', 'input_data', 'output_data', 'status',
                 'created_at', 'updated_at']
        read_only_fields = fields

class ContentGenerationSerializer(serializers.Serializer):
    """Serializer for content generation requests"""
    content_type = serializers.ChoiceField(
        choices=['post', 'caption', 'hashtag'],
        required=False
    )
    prompt = serializers.CharField(max_length=1000)
    platform = serializers.ChoiceField(
        choices=['general', 'twitter', 'instagram', 'facebook', 'linkedin'],
        default='general'
    )
    tone = serializers.ChoiceField(
        choices=['professional', 'casual', 'friendly', 'formal', 'humorous'],
        default='professional'
    )
    length = serializers.ChoiceField(
        choices=['short', 'medium', 'long'],
        default='medium'
    )
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        max_length=10
    )
    language = serializers.CharField(
        max_length=10,
        default='en'
    )
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high'],
        default='normal'
    )

    def validate_prompt(self, value):
        """Validate prompt length"""
        min_length = 10
        max_length = 1000

        if len(value) < min_length:
            raise serializers.ValidationError(
                f'Prompt must be at least {min_length} characters long'
            )
        if len(value) > max_length:
            raise serializers.ValidationError(
                f'Prompt cannot exceed {max_length} characters'
            )
        return value

    def validate_keywords(self, value):
        """Validate keywords"""
        if value and len(value) > 10:
            raise serializers.ValidationError(
                'Maximum 10 keywords allowed'
            )
        return value

class SentimentAnalysisSerializer(serializers.Serializer):
    """Serializer for sentiment analysis requests"""
    text = serializers.CharField(max_length=5000)
    context = serializers.ChoiceField(
        choices=['comment', 'feedback', 'message', 'review'],
        default='comment'
    )
    language = serializers.CharField(
        max_length=10,
        default='en'
    )
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high'],
        default='normal'
    )
    include_emotions = serializers.BooleanField(default=True)
    detailed_analysis = serializers.BooleanField(default=False)

    def validate_text(self, value):
        """Validate text length"""
        min_length = 5
        max_length = 5000

        if len(value) < min_length:
            raise serializers.ValidationError(
                f'Text must be at least {min_length} characters long'
            )
        if len(value) > max_length:
            raise serializers.ValidationError(
                f'Text cannot exceed {max_length} characters'
            )
        return value