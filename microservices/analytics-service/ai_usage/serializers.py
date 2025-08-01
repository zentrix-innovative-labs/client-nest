from rest_framework import serializers
from .models import AIUsageLog

class AIUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIUsageLog
        fields = '__all__' 