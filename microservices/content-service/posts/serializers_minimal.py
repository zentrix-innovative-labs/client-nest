from rest_framework import serializers
from .models_minimal import Post

class PostSerializer(serializers.ModelSerializer):
    """Basic serializer for Post model"""
    
    user_username = serializers.ReadOnlyField(source='user.username')
    engagement_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'user_username', 'title', 'content', 'status',
            'post_type', 'view_count', 'like_count', 'comment_count',
            'share_count', 'engagement_rate', 'created_at', 'updated_at',
            'published_at', 'scheduled_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_username', 'view_count', 'like_count',
            'comment_count', 'share_count', 'engagement_rate', 'created_at',
            'updated_at', 'published_at'
        ]

class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'status', 'post_type', 'scheduled_at']
    
    def create(self, validated_data):
        return super().create(validated_data)

class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating posts"""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'status', 'post_type', 'scheduled_at'] 