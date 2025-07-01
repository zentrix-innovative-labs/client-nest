from rest_framework import serializers

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
    call_to_action = serializers.CharField()
    suggestions = serializers.ListField(child=serializers.CharField(), required=False)
    variations = serializers.ListField(child=serializers.CharField(), required=False)
    quality_score = serializers.IntegerField()
    safety_check = serializers.DictField()
    readability_score = serializers.FloatField()
    engagement_prediction = serializers.CharField()
    optimal_posting_time_suggestion = serializers.CharField() 