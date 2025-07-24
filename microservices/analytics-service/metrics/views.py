from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RawEvent, AggregatedMetric
from .serializers import RawEventSerializer, AggregatedMetricSerializer
from django.db.models import Sum, Avg

# Create your views here.

class RawEventCreateView(generics.CreateAPIView):
    queryset = RawEvent.objects.all()
    serializer_class = RawEventSerializer
    permission_classes = [permissions.IsAuthenticated]

class RawEventListView(generics.ListAPIView):
    queryset = RawEvent.objects.all().order_by('-timestamp')
    serializer_class = RawEventSerializer
    permission_classes = [permissions.IsAuthenticated]

class AggregatedMetricListView(generics.ListAPIView):
    queryset = AggregatedMetric.objects.all().order_by('-period')
    serializer_class = AggregatedMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

class AggregatedMetricAggregateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Example: sum and average of metric values by type
        sum_by_type = AggregatedMetric.objects.values('metric_type').annotate(total=Sum('value'))
        avg_by_type = AggregatedMetric.objects.values('metric_type').annotate(avg=Avg('value'))
        return Response({
            'sum_by_type': list(sum_by_type),
            'avg_by_type': list(avg_by_type),
        })
