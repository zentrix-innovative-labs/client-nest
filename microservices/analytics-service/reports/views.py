from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer

# Create your views here.

class ReportListCreateView(generics.ListCreateAPIView):
    queryset = Report.objects.all().order_by('-generated_at')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Stub: In a real implementation, trigger async report generation (e.g., with Celery)
        serializer.save(user=self.request.user, status='generating')

class ReportRetrieveView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
