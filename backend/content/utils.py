from .models import CommentLike
from django.db import transaction
from django.db.models import F

def toggle_comment_like(comment, user):
    """
    Like or unlike a comment. Returns (action, like_count).
    """
    with transaction.atomic():
        try:
            like = CommentLike.objects.get(comment=comment, user=user)
            like.delete()
            action = 'unliked'
            comment.like_count = F('like_count') - 1
        except CommentLike.DoesNotExist:
            CommentLike.objects.create(comment=comment, user=user)
            action = 'liked'
            comment.like_count = F('like_count') + 1
        comment.save(update_fields=['like_count'])
        comment.refresh_from_db(fields=['like_count'])
    return action, comment.like_count 