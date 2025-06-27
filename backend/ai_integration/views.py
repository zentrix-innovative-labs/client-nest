from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from celery.result import AsyncResult
from .serializers import ContentGenerationRequestSerializer, ContentGenerationResponseSerializer
from .tasks import generate_content_task

# Create your views here.

class ContentGenerationAPIView(APIView):
    """
    POST endpoint to asynchronously trigger AI content generation.
    This view dispatches a Celery task and returns a task ID.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ContentGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        
        # Dispatch the task to Celery
        task = generate_content_task.delay(
            user_id=request.user.id,
            validated_data=validated_data
        )

        return Response(
            {"task_id": task.id},
            status=status.HTTP_202_ACCEPTED
        )

class TaskStatusAPIView(APIView):
    """
    GET endpoint to check the status and result of a Celery task.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        task_result = AsyncResult(task_id)

        response_data = {
            'task_id': task_id,
            'status': task_result.status,
            'result': None
        }

        if task_result.successful():
            # If successful, the result is the generated content dictionary
            result = task_result.get()
            response_serializer = ContentGenerationResponseSerializer(data=result)
            if response_serializer.is_valid():
                response_data['result'] = response_serializer.data
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # The AI service returned data in an unexpected format.
                response_data['status'] = 'FAILURE'
                response_data['result'] = {'error': 'AI response structure was invalid.', 'details': response_serializer.errors}
                return Response(response_data, status=status.HTTP_502_BAD_GATEWAY)

        elif task_result.failed():
            # The task execution failed with an exception.
            response_data['result'] = {'error': str(task_result.info)}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            # Task is PENDING, STARTED, RETRY, etc.
            # Inform the client that the request is accepted and processing.
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
