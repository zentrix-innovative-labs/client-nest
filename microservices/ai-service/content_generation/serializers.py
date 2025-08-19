# microservices/ai-service/content_generation/serializers.py
from rest_framework import serializers
from .models import GeneratedContent, ContentTemplate, AIUsageLog

class ContentGenerationRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=256)
    platform = serializers.ChoiceField(choices=[
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
    ])
    tone = serializers.ChoiceField(choices=[
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('witty', 'Witty'),
        ('inspirational', 'Inspirational'),
    ], default='professional')
    content_type = serializers.CharField(max_length=32, default='post')
    additional_context = serializers.CharField(max_length=512, required=False, allow_blank=True)

class ContentGenerationResponseSerializer(serializers.Serializer):
    content = serializers.CharField()
    hashtags = serializers.ListField(child=serializers.CharField())
    call_to_action = serializers.CharField(required=False, allow_blank=True)
    suggestions = serializers.ListField(child=serializers.CharField(), required=False)
    variations = serializers.ListField(child=serializers.DictField(), required=False)  # Changed to DictField
    quality_score = serializers.IntegerField()
    safety_check = serializers.DictField()
    readability_score = serializers.FloatField()
    engagement_prediction = serializers.CharField()
    optimal_posting_time_suggestion = serializers.CharField()

class GeneratedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedContent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ContentTemplateSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = ContentTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AIUsageLogSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = AIUsageLog
        fields = '__all__'
        read_only_fields = ['created_at'] 