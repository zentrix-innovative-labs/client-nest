from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AIUsageLog
from .serializers import AIUsageLogSerializer
from django.db.models import Sum, Avg

# Create your views here.

class AIUsageLogListView(generics.ListAPIView):
    queryset = AIUsageLog.objects.all().order_by('-timestamp')
    serializer_class = AIUsageLogSerializer
    permission_classes = [permissions.IsAuthenticated]

class AIUsageAggregateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_cost = AIUsageLog.objects.aggregate(total_cost=Sum('cost'))['total_cost'] or 0
        avg_duration = AIUsageLog.objects.aggregate(avg_duration=Avg('duration_ms'))['avg_duration'] or 0
        cost_per_user = AIUsageLog.objects.values('user').annotate(user_cost=Sum('cost'))
        avg_duration_per_model = AIUsageLog.objects.values('model_name').annotate(model_avg_duration=Avg('duration_ms'))
        return Response({
            'total_cost': total_cost,
            'avg_duration_ms': avg_duration,
            'cost_per_user': list(cost_per_user),
            'avg_duration_per_model': list(avg_duration_per_model),
        })
