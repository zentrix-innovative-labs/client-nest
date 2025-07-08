from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    SocialAccount,
    Post,
    PostMedia,
    PostPlatform,
    Comment
)

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = [
        'platform',
        'platform_username',
        'user',
        'team',
        'is_active',
        'created_at',
        'token_expires_at'
    ]
    list_filter = [
        'platform',
        'is_active',
        'created_at',
        'token_expires_at'
    ]
    search_fields = [
        'platform_username',
        'platform_user_id',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'platform_user_id'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'platform',
                'platform_username',
                'platform_user_id',
                'user',
                'team'
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'token_expires_at'
            )
        }),
        ('Metadata', {
            'fields': (
                'platform_data',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'team')

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 0
    readonly_fields = ['id', 'created_at']
    fields = [
        'media_type',
        'file_url',
        'thumbnail_url',
        'alt_text',
        'order',
        'created_at'
    ]

class PostPlatformInline(admin.TabularInline):
    model = PostPlatform
    extra = 0
    readonly_fields = [
        'id',
        'status',
        'published_at',
        'platform_post_id',
        'platform_url',
        'created_at'
    ]
    fields = [
        'social_account',
        'status',
        'platform_specific_content',
        'platform_post_id',
        'platform_url',
        'published_at',
        'error_message'
    ]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'user',
        'team',
        'type',
        'status',
        'platform_count',
        'engagement_summary',
        'scheduled_at',
        'published_at',
        'created_at'
    ]
    list_filter = [
        'status',
        'type',
        'created_at',
        'scheduled_at',
        'published_at',
        'user',
        'team'
    ]
    search_fields = [
        'title',
        'content',
        'hashtags',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'published_at',
        'view_count',
        'like_count',
        'comment_count',
        'share_count'
    ]
    inlines = [PostMediaInline, PostPlatformInline]
    
    fieldsets = (
        ('Content', {
            'fields': (
                'id',
                'title',
                'content',
                'hashtags',
                'type'
            )
        }),
        ('Ownership', {
            'fields': (
                'user',
                'team'
            )
        }),
        ('Publishing', {
            'fields': (
                'status',
                'scheduled_at',
                'published_at',
                'error_message'
            )
        }),
        ('Analytics', {
            'fields': (
                'view_count',
                'like_count',
                'comment_count',
                'share_count'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'metadata',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'team'
        ).prefetch_related('platforms', 'media')
    
    def platform_count(self, obj):
        return obj.platforms.count()
    platform_count.short_description = 'Platforms'
    
    def engagement_summary(self, obj):
        total_engagement = obj.like_count + obj.comment_count + obj.share_count
        if total_engagement > 0:
            return format_html(
                '<span style="color: green;">👍 {} 💬 {} 🔄 {}</span>',
                obj.like_count,
                obj.comment_count,
                obj.share_count
            )
        return '-'
    engagement_summary.short_description = 'Engagement'
    
    actions = ['publish_posts', 'schedule_posts', 'duplicate_posts']
    
    def publish_posts(self, request, queryset):
        from .tasks import publish_post_task
        
        published_count = 0
        for post in queryset.filter(status__in=['draft', 'scheduled']):
            post.status = 'published'
            post.save()
            publish_post_task.delay(str(post.id))
            published_count += 1
        
        self.message_user(
            request,
            f'{published_count} posts queued for publishing.'
        )
    publish_posts.short_description = 'Publish selected posts'
    
    def schedule_posts(self, request, queryset):
        # This would need a form to get the scheduled time
        self.message_user(
            request,
            'Scheduling posts requires individual editing to set scheduled time.'
        )
    schedule_posts.short_description = 'Schedule selected posts'
    
    def duplicate_posts(self, request, queryset):
        duplicated_count = 0
        for post in queryset:
            # Create duplicate
            post.pk = None
            post.title = f"{post.title} (Copy)"
            post.status = 'draft'
            post.scheduled_at = None
            post.published_at = None
            post.save()
            duplicated_count += 1
        
        self.message_user(
            request,
            f'{duplicated_count} posts duplicated.'
        )
    duplicate_posts.short_description = 'Duplicate selected posts'

@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = [
        'post',
        'media_type',
        'file_name',
        'file_size_display',
        'order',
        'created_at'
    ]
    list_filter = [
        'media_type',
        'created_at'
    ]
    search_fields = [
        'post__title',
        'file_url',
        'alt_text'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'file_size_display'
    ]
    
    fieldsets = (
        ('Media Information', {
            'fields': (
                'id',
                'post',
                'media_type',
                'file_url',
                'thumbnail_url',
                'file_size_display'
            )
        }),
        ('Display', {
            'fields': (
                'alt_text',
                'order'
            )
        }),
        ('Metadata', {
            'fields': (
                'metadata',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post')
    
    def file_name(self, obj):
        if obj.file_url:
            return obj.file_url.split('/')[-1]
        return '-'
    file_name.short_description = 'File Name'
    
    def file_size_display(self, obj):
        if hasattr(obj, 'file_size') and obj.file_size:
            # Convert bytes to human readable format
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return '-'
    file_size_display.short_description = 'File Size'

@admin.register(PostPlatform)
class PostPlatformAdmin(admin.ModelAdmin):
    list_display = [
        'post',
        'platform_name',
        'status',
        'published_at',
        'platform_post_id',
        'analytics_summary',
        'created_at'
    ]
    list_filter = [
        'status',
        'social_account__platform',
        'published_at',
        'created_at'
    ]
    search_fields = [
        'post__title',
        'social_account__platform_username',
        'platform_post_id',
        'platform_url'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'published_at',
        'platform_post_id',
        'platform_url',
        'last_analytics_update'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'post',
                'social_account',
                'status'
            )
        }),
        ('Platform Content', {
            'fields': (
                'platform_specific_content',
                'platform_post_id',
                'platform_url'
            )
        }),
        ('Publishing', {
            'fields': (
                'published_at',
                'error_message'
            )
        }),
        ('Analytics', {
            'fields': (
                'platform_analytics',
                'last_analytics_update'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'post', 'social_account'
        )
    
    def platform_name(self, obj):
        return f"{obj.social_account.platform} (@{obj.social_account.platform_username})"
    platform_name.short_description = 'Platform'
    
    def analytics_summary(self, obj):
        if obj.platform_analytics:
            analytics = obj.platform_analytics
            views = analytics.get('views', 0)
            likes = analytics.get('likes', 0)
            comments = analytics.get('comments', 0)
            if views > 0 or likes > 0 or comments > 0:
                return format_html(
                    '<span style="color: blue;">👁 {} 👍 {} 💬 {}</span>',
                    views, likes, comments
                )
        return '-'
    analytics_summary.short_description = 'Analytics'
    
    actions = ['sync_analytics', 'republish_failed']
    
    def sync_analytics(self, request, queryset):
        from .tasks import sync_post_analytics_task
        
        synced_count = 0
        for post_platform in queryset.filter(
            status='published',
            platform_post_id__isnull=False
        ):
            sync_post_analytics_task.delay(str(post_platform.id))
            synced_count += 1
        
        self.message_user(
            request,
            f'{synced_count} analytics sync tasks queued.'
        )
    sync_analytics.short_description = 'Sync analytics for selected platforms'
    
    def republish_failed(self, request, queryset):
        from .tasks import publish_post_task
        
        republished_count = 0
        for post_platform in queryset.filter(status='failed'):
            post_platform.status = 'draft'
            post_platform.error_message = ''
            post_platform.save()
            publish_post_task.delay(str(post_platform.post.id))
            republished_count += 1
        
        self.message_user(
            request,
            f'{republished_count} failed posts queued for republishing.'
        )
    republish_failed.short_description = 'Republish failed posts'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'post_title',
        'platform_name',
        'author_name',
        'content_preview',
        'created_at',
        'platform_created_at'
    ]
    list_filter = [
        'post_platform__social_account__platform',
        'created_at',
        'platform_created_at'
    ]
    search_fields = [
        'post_platform__post__title',
        'author_name',
        'content',
        'platform_comment_id'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'platform_comment_id',
        'platform_created_at'
    ]
    
    fieldsets = (
        ('Comment Information', {
            'fields': (
                'id',
                'post_platform',
                'platform_comment_id',
                'author_name',
                'content'
            )
        }),
        ('Timestamps', {
            'fields': (
                'platform_created_at',
                'created_at',
                'updated_at'
            )
        }),
        ('Metadata', {
            'fields': (
                'metadata',
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'post_platform__post',
            'post_platform__social_account'
        )
    
    def post_title(self, obj):
        return obj.post_platform.post.title
    post_title.short_description = 'Post'
    
    def platform_name(self, obj):
        return obj.post_platform.social_account.platform
    platform_name.short_description = 'Platform'
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = 'Content'

# Customize admin site headers
admin.site.site_header = 'ClientNest Content Service Admin'
admin.site.site_title = 'Content Service Admin'
admin.site.index_title = 'Content Management'