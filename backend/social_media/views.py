from django.shortcuts import render
from rest_framework import viewsets
from .models import Post, Comment, Engagement
from .serializers import PostSerializer, CommentSerializer, EngagementSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

class EngagementViewSet(viewsets.ModelViewSet):
    queryset = Engagement.objects.all()
    serializer_class = EngagementSerializer
    permission_classes = [IsAuthenticated]
