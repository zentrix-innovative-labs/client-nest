from celery import shared_task
from user_service.models import User
from ai_service.content_generation.logic import content_serviceGenerator
from ai_service.common.deepseek_client import DeepSeekClient, AIClientError

# Define a custom exception for task-specific failures
class TaskFailureError(Exception):
    pass

@shared_task(bind=True)
def generate_content_task(self, user_id: int, validated_data: dict):
    """
    Celery task to generate content asynchronously.
    Raises exceptions for proper error handling in Celery.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as e:
        raise TaskFailureError(f"User with id={user_id} not found.") from e

    try:
        client = DeepSeekClient()
        generator = ContentGenerator(client)
        
        result_data = generator.generate_post(user=user, **validated_data)
        
        if "error" in result_data:
            raise TaskFailureError(result_data["error"])

        return result_data

    except AIClientError as e:
        raise TaskFailureError(f"AI Client Error: {e}") from e
    except (TypeError, ValueError) as e:
        # Handle specific, potentially recoverable errors during task execution.
        raise TaskFailureError(f'A task-specific error occurred: {str(e)}') from e
    except Exception as e:
        # Re-raise any other unexpected errors for full visibility.
        # This prevents masking critical, unforeseen issues.
        raise e 
