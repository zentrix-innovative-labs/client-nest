from django.urls import path
from .views import (
    RawEventCreateView, RawEventListView,
    AggregatedMetricListView, AggregatedMetricAggregateView
)

urlpatterns = [
    path('events/', RawEventListView.as_view(), name='metrics-raw-event-list'),
    path('events/ingest/', RawEventCreateView.as_view(), name='metrics-raw-event-create'),
    path('aggregated/', AggregatedMetricListView.as_view(), name='metrics-aggregated-list'),
    path('aggregated/aggregate/', AggregatedMetricAggregateView.as_view(), name='metrics-aggregated-aggregate'),
] 