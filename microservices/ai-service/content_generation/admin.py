# microservices/ai-service/content_generation/admin.py
from django.contrib import admin
from .models import GeneratedContent, ContentTemplate, AIUsageLog

@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'platform', 'tone', 'quality_score', 'created_at']
    list_filter = ['platform', 'tone', 'quality_score', 'created_at']
    search_fields = ['topic', 'content', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(ContentTemplate)
class ContentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'tone', 'created_by', 'is_active', 'created_at']
    list_filter = ['platform', 'tone', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'request_type', 'total_tokens', 'cost', 'response_time_ms', 'created_at']
    list_filter = ['request_type', 'created_at']
    search_fields = ['user__username', 'request_type']
    readonly_fields = ['created_at']
    ordering = ['-created_at'] 