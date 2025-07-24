from rest_framework import serializers
from .models import AnalyticsEvent, AggregatedMetrics, Report

class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = '__all__'

class AggregatedMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedMetrics
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__' 