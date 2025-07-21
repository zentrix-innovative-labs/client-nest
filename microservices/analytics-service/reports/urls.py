from django.urls import path
from .views import ReportListCreateView, ReportRetrieveView

urlpatterns = [
    path('', ReportListCreateView.as_view(), name='report-list-create'),
    path('<int:pk>/', ReportRetrieveView.as_view(), name='report-detail'),
] 