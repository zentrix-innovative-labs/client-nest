# views.py
import json
from datetime import datetime
from collections import defaultdict

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
import pytz
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@login_required
def post_timing_optimization(request):
    """
    Analyze post engagement data to recommend optimal posting times.
    Requires authentication and accepts POST requests only.
    """
    try:
        # Parse request data
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON format in request body.'
            }, status=400)
        
        posts = data.get("posts", [])

        if not posts:
            return JsonResponse({
                "error": "No posts provided. Please provide a list of posts with engagement data."
            }, status=400)

        if not isinstance(posts, list):
            return JsonResponse({
                "error": "Posts must be provided as a list."
            }, status=400)

        if len(posts) < 5:
            return JsonResponse({
                "error": "At least 5 posts are required for meaningful analysis."
            }, status=400)

        engagement_by_slot = defaultdict(list)
        processed_posts = 0
        skipped_posts = 0

        for i, post in enumerate(posts):
            try:
                # Validate post structure
                if not isinstance(post, dict):
                    logger.warning(f"Post {i} is not a dictionary, skipping")
                    skipped_posts += 1
                    continue

                timestamp = post.get("timestamp")
                likes = post.get("likes", 0)
                comments = post.get("comments", 0)
                shares = post.get("shares", 0)

                # Validate required fields
                if not timestamp:
                    logger.warning(f"Post {i} missing timestamp, skipping")
                    skipped_posts += 1
                    continue

                # Validate numeric fields
                try:
                    likes = int(likes) if likes is not None else 0
                    comments = int(comments) if comments is not None else 0
                    shares = int(shares) if shares is not None else 0
                except (ValueError, TypeError):
                    logger.warning(f"Post {i} has invalid numeric values, using defaults")
                    likes = comments = shares = 0

                # Parse timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = make_aware(dt, timezone=pytz.UTC)
                    else:
                        dt = dt.astimezone(pytz.UTC)
                    
                    day = dt.strftime('%A')
                    hour = dt.strftime('%H:00')
                    slot = f"{day} {hour}"
                    
                    # Calculate engagement score
                    engagement_score = likes + (2 * comments) + (3 * shares)
                    engagement_by_slot[slot].append(engagement_score)
                    processed_posts += 1
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Post {i} has malformed timestamp '{timestamp}': {e}")
                    skipped_posts += 1
                    continue

            except Exception as e:
                logger.warning(f"Error processing post {i}: {e}")
                skipped_posts += 1
                continue

        # Check if we have enough data
        if len(engagement_by_slot) < 3:
            return JsonResponse({
                "error": "Insufficient data for analysis. Need posts from at least 3 different time slots."
            }, status=400)

        # Calculate average engagement scores
        average_scores = {}
        for slot, scores in engagement_by_slot.items():
            if len(scores) > 0:
                average_scores[slot] = sum(scores) / len(scores)

        if not average_scores:
            return JsonResponse({
                "error": "No valid engagement data found."
            }, status=400)

        # Get top 3 time slots
        top_slots = sorted(average_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        # Calculate overall average for normalization
        overall_average = sum(average_scores.values()) / len(average_scores)

        response_data = [
            {
                "slot": slot,
                "engagement_boost": round(score / overall_average, 2) if overall_average > 0 else 1.0,
                "average_engagement": round(score, 2),
                "post_count": len(engagement_by_slot[slot])
            }
            for slot, score in top_slots
        ]

        # Log successful analysis
        logger.info(f"Post timing analysis completed for user {request.user.username}. "
                   f"Processed {processed_posts} posts, skipped {skipped_posts} posts. "
                   f"Found {len(engagement_by_slot)} time slots.")

        return JsonResponse({
            "success": True,
            "recommended_times": response_data,
            "analysis_summary": {
                "total_posts_processed": processed_posts,
                "posts_skipped": skipped_posts,
                "time_slots_analyzed": len(engagement_by_slot),
                "overall_average_engagement": round(overall_average, 2)
            }
        })

    except Exception as e:
        # Log the full error details for debugging
        logger.error(f"Unexpected error in post_timing_optimization for user {request.user.username}: {e}", exc_info=True)
        
        # Return generic error message to avoid exposing internal details
        return JsonResponse({
            "error": "An unexpected error occurred while analyzing post timing. Please try again later."
        }, status=500)
