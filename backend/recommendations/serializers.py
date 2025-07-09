from rest_framework import serializers
from .models import UserInteraction, Recommendation, ChurnPrediction

class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = ['id', 'user', 'interaction_type', 'content_id', 'content_type', 
                 'platform', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'content_id', 'content_type', 'score', 'algorithm',
                 'is_clicked', 'is_dismissed', 'created_at']
        read_only_fields = ['id', 'score', 'created_at']

class ChurnPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurnPrediction
        fields = ['id', 'user', 'churn_risk', 'features', 'prediction_date']
        read_only_fields = ['id', 'prediction_date']

class RecommendationRequestSerializer(serializers.Serializer):
    algorithm = serializers.ChoiceField(
        choices=['collaborative', 'content', 'hybrid'],
        default='hybrid'
    )
    top_k = serializers.IntegerField(min_value=1, max_value=50, default=10)

class ChurnPredictionRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class RecommendationResponseSerializer(serializers.Serializer):
    recommendations = serializers.ListField(
        child=serializers.DictField()
    )
    algorithm = serializers.CharField()
    total_count = serializers.IntegerField()

class ChurnPredictionResponseSerializer(serializers.Serializer):
    churn_risk = serializers.FloatField()
    risk_level = serializers.CharField()
    recommendations = serializers.ListField(
        child=serializers.CharField(),
        required=False
    ) 