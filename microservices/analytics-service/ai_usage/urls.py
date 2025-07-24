from django.urls import path
from .views import AIUsageLogListView, AIUsageAggregateView

urlpatterns = [
    path('logs/', AIUsageLogListView.as_view(), name='ai-usage-log-list'),
    path('aggregate/', AIUsageAggregateView.as_view(), name='ai-usage-aggregate'),
] 