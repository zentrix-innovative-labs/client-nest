from django.urls import path
from .views import content_serviceGenerationAPIView, TaskStatusAPIView

urlpatterns = [
    path('generate-content/', ContentGenerationAPIView.as_view(), name='generate-content'),
    path('task-status/<str:task_id>/', TaskStatusAPIView.as_view(), name='task-status'),
] 
