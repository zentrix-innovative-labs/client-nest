from rest_framework.views import APIView
from rest_framework.response import Response
from tasks.tasks import add

class AddTaskView(APIView):
    def post(self, request):
        x = int(request.data.get('x', 0))
        y = int(request.data.get('y', 0))
        result = add.delay(x, y)
        return Response({'task_id': result.id})

class TaskStatusView(APIView):
    def get(self, request, task_id):
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        return Response({'status': result.status, 'result': result.result})
