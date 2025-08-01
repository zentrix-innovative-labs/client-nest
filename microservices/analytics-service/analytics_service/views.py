from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from .models import AggregatedMetrics, Report
from .serializers import AggregatedMetricsSerializer, ReportSerializer
from .ml.predictors import predict_engagement
from .ml.insights import generate_insights

class DashboardView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AggregatedMetricsSerializer

    def get_queryset(self):
        return AggregatedMetrics.objects.filter(metric_type='dashboard')

class EngagementInputSerializer(serializers.Serializer):
    features = serializers.ListField(
        child=serializers.FloatField(),
        min_length=3, max_length=3,
        help_text="Feature vector of length 3"
    )

class EngagementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EngagementInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        features = serializer.validated_data['features']
        prediction = predict_engagement(features)
        return Response({'prediction': prediction})

class AudienceView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AggregatedMetricsSerializer

    def get_queryset(self):
        return AggregatedMetrics.objects.filter(metric_type='audience')

class CustomReportView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs):
        # Custom report generation logic can be added here
        return super().create(request, *args, **kwargs)

class InsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        insights = generate_insights()
        return Response({'insights': insights}) 