# views.py
import json
from datetime import datetime
from collections import defaultdict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.timezone import make_aware
import pytz
import logging

@csrf_exempt
@require_http_methods(["POST"])
def post_timing_optimization(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        posts = data.get("posts", [])

        if not posts:
            return JsonResponse({"error": "No posts provided."}, status=400)

        engagement_by_slot = defaultdict(list)

        for post in posts:
            timestamp = post.get("timestamp")
            likes = int(post.get("likes", 0))
            comments = int(post.get("comments", 0))
            shares = int(post.get("shares", 0))

            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = make_aware(dt, timezone=pytz.UTC)
                else:
                    dt = dt.astimezone(pytz.UTC)
                day = dt.strftime('%A')
                hour = dt.strftime('%H:00')
                slot = f"{day} {hour}"
                engagement_score = likes + (2 * comments) + (3 * shares)
                engagement_by_slot[slot].append(engagement_score)
            except (ValueError, TypeError) as e:
                logging.error(f"Malformed timestamp '{timestamp}': {e}")
                continue  # Skip malformed timestamps

        average_scores = {
            slot: sum(scores) / len(scores) for slot, scores in engagement_by_slot.items()
        }

        top_slots = sorted(average_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        response_data = [
            {
                "slot": slot,
                "engagement_boost": round(score / 100, 2)  # Normalized
            }
            for slot, score in top_slots
        ]

        return JsonResponse({"recommended_times": response_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# urls.py
from django.urls import path
from .views import post_timing_optimization

urlpatterns = [
    path('api/v1/ai/post-timing/', post_timing_optimization, name='post_timing_optimization'),
]
