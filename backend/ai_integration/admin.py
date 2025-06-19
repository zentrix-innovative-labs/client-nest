from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import AIModel, AITask

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    """Admin interface for AI models"""
    list_display = ['name', 'version', 'description', 'created_at', 'updated_at']
    list_filter = ['version', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = [
        ('Model Information', {
            'fields': ['name', 'version', 'description']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(AITask)
class AITaskAdmin(admin.ModelAdmin):
    """Admin interface for AI tasks"""
    list_display = ['id', 'model_link', 'user_link', 'status', 'task_type',
                   'created_at', 'processing_time']
    list_filter = ['status', 'model', 'created_at']
    search_fields = ['id', 'user__username', 'model__name']
    readonly_fields = ['created_at', 'updated_at', 'processing_time']
    ordering = ['-created_at']

    fieldsets = [
        ('Task Information', {
            'fields': ['model', 'user', 'status']
        }),
        ('Data', {
            'fields': ['input_data', 'output_data'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'processing_time'],
            'classes': ['collapse']
        })
    ]

    def model_link(self, obj):
        """Create a link to the related AI model"""
        url = reverse('admin:ai_integration_aimodel_change', args=[obj.model.id])
        return format_html('<a href="{}">{}</a>', url, obj.model.name)
    model_link.short_description = 'Model'
    model_link.admin_order_field = 'model__name'

    def user_link(self, obj):
        """Create a link to the related user"""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'

    def task_type(self, obj):
        """Get the task type from input data"""
        return obj.input_data.get('type', 'Unknown')
    task_type.short_description = 'Task Type'

    def processing_time(self, obj):
        """Calculate task processing time"""
        if obj.status == 'completed' and obj.updated_at and obj.created_at:
            time_diff = obj.updated_at - obj.created_at
            return f'{time_diff.total_seconds():.2f}s'
        return '-'
    processing_time.short_description = 'Processing Time'

    def get_queryset(self, request):
        """Optimize queryset by prefetching related objects"""
        return super().get_queryset(request).select_related('model', 'user')

    class Media:
        css = {
            'all': ['admin/css/ai_integration.css']
        }
        js = ['admin/js/ai_integration.js']
