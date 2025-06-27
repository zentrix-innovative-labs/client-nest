from celery import shared_task
import asyncio
from users.models import User
from ai_services.content_generation.logic import ContentGenerator
from ai_services.common.deepseek_client import DeepSeekClient, AIClientError

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
        
        # Run the async method in the synchronous Celery task
        result_data = asyncio.run(generator.generate_post(user=user, **validated_data))
        
        if "error" in result_data:
            raise TaskFailureError(result_data["error"])

        return result_data

    except AIClientError as e:
        raise TaskFailureError(f"AI Client Error: {e}") from e
    except Exception as e:
        # Catch any other unexpected errors and re-raise for visibility
        raise TaskFailureError(f'An unexpected error occurred in the task: {str(e)}') from e 