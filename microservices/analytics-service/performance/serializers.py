from rest_framework import serializers
from .models import APIMetric, ErrorLog

class APIMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIMetric
        fields = '__all__'

class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = '__all__' 