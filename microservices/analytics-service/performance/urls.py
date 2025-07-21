from django.urls import path
from .views import APIMetricListView, ErrorLogListView, APIMetricAggregateView

urlpatterns = [
    path('metrics/', APIMetricListView.as_view(), name='performance-metrics-list'),
    path('errors/', ErrorLogListView.as_view(), name='performance-errors-list'),
    path('aggregate/', APIMetricAggregateView.as_view(), name='performance-metrics-aggregate'),
] 