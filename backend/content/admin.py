from django.contrib import admin
from .models import Post, Schedule, Comment, CommentLike

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'status', 'created_at', 'published_at')
    list_filter = ('status', 'created_at', 'published_at')
    search_fields = ('content', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'content', 'like_count', 'is_edited', 'created_at')
    list_filter = ('is_edited', 'created_at', 'edited_at', 'post__status')
    search_fields = ('content', 'author__username', 'post__content')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'like_count', 'is_edited', 'edited_at', 'created_at', 'updated_at')
    raw_id_fields = ('post', 'author', 'parent_comment')

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment__content', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    raw_id_fields = ('comment', 'user')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('post', 'platform', 'scheduled_time', 'is_published', 'created_at')
    list_filter = ('platform', 'is_published', 'scheduled_time', 'created_at')
    search_fields = ('post__content', 'platform')
    date_hierarchy = 'scheduled_time'
    readonly_fields = ('created_at',)
    raw_id_fields = ('post',)
