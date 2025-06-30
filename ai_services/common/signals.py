from django.dispatch import Signal

# Signal to log AI usage, with arguments for user, cost, and metadata
ai_usage_logged = Signal(providing_args=["user", "cost", "metadata"]) 