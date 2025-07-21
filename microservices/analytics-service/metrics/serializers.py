from rest_framework import serializers
from .models import RawEvent, AggregatedMetric

class RawEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawEvent
        fields = '__all__'

class AggregatedMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedMetric
        fields = '__all__' 