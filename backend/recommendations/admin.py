from django.contrib import admin
from .models import UserInteraction, Recommendation, ChurnPrediction

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'interaction_type', 'content_id', 'content_type', 'platform', 'created_at']
    list_filter = ['interaction_type', 'content_type', 'platform', 'created_at']
    search_fields = ['user__username', 'user__email', 'content_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_id', 'content_type', 'score', 'algorithm', 'is_clicked', 'is_dismissed', 'created_at']
    list_filter = ['algorithm', 'content_type', 'is_clicked', 'is_dismissed', 'created_at']
    search_fields = ['user__username', 'user__email', 'content_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(ChurnPrediction)
class ChurnPredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'churn_risk', 'prediction_date']
    list_filter = ['prediction_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['prediction_date']
    date_hierarchy = 'prediction_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user') 