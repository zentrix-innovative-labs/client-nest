from django.test import TestCase
from analytics_service.models import AnalyticsEvent, AggregatedMetrics, Report

class AnalyticsModelTests(TestCase):
    def test_create_analytics_event(self):
        event = AnalyticsEvent.objects.create(event_type='test', user_id=1, platform='test', data={})
        self.assertIsNotNone(event.id)

    def test_create_aggregated_metrics(self):
        metric = AggregatedMetrics.objects.create(date='2024-01-01', metric_type='dashboard', value=1.0, platform='test')
        self.assertIsNotNone(metric.id)

    def test_create_report(self):
        report = Report.objects.create(user_id=1, report_type='summary', data={})
        self.assertIsNotNone(report.id) 