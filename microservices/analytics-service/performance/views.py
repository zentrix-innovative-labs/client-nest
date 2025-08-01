from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import APIMetric, ErrorLog
from .serializers import APIMetricSerializer, ErrorLogSerializer
from django.db.models import Avg, Count

# Create your views here.

class APIMetricListView(generics.ListAPIView):
    queryset = APIMetric.objects.all().order_by('-timestamp')
    serializer_class = APIMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

class ErrorLogListView(generics.ListAPIView):
    queryset = ErrorLog.objects.all().order_by('-timestamp')
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated]

class APIMetricAggregateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        avg_response = APIMetric.objects.values('endpoint').annotate(avg_response_time=Avg('response_time_ms'))
        error_counts = ErrorLog.objects.values('endpoint').annotate(error_count=Count('id'))
        return Response({
            'average_response_time': list(avg_response),
            'error_counts': list(error_counts),
        })
