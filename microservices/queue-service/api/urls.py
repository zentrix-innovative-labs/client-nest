from django.urls import path
from .views import AddTaskView, TaskStatusView

urlpatterns = [
    path('add/', AddTaskView.as_view()),
    path('status/<str:task_id>/', TaskStatusView.as_view()),
]
