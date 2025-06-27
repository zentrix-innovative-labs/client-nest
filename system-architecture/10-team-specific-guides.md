# Team-Specific Implementation Guides

This document provides detailed implementation guides for each team working on ClientNest, designed for second-year computer science students and interns.

## Table of Contents

1. [Backend Team (Django) Guide](#backend-team-django-guide)
2. [Frontend Team (React) Guide](#frontend-team-react-guide)
3. [Data Science Team Guide](#data-science-team-guide)
4. [AI Team Guide](#ai-team-guide)
5. [Security Team Guide](#security-team-guide)
6. [Cross-Team Collaboration](#cross-team-collaboration)

---

## Backend Team (Django) Guide

### Overview
The backend team is responsible for building the core API services, database management, and server-side logic using Django and Django REST Framework.

### Project Structure
```
clientnest-backend/
├── manage.py
├── requirements.txt
├── clientnest/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   ├── social/
│   ├── ai/
│   ├── analytics/
│   ├── billing/
│   └── core/
└── tests/
```

### Key Responsibilities

#### 1. User Management System
```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]
    
    email = models.EmailField(unique=True)
    subscription_tier = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_TIERS, 
        default='free'
    )
    ai_tokens_used = models.IntegerField(default=0)
    ai_tokens_limit = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    notification_preferences = models.JSONField(default=dict)
```

#### 2. Social Media Integration
```python
# apps/social/models.py
from django.db import models
from django.conf import settings

class SocialMediaAccount(models.Model):
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('tiktok', 'TikTok'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_user_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'platform', 'platform_user_id']

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE)
    content = models.TextField()
    media_urls = models.JSONField(default=list)
    platform_post_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    ai_generated = models.BooleanField(default=False)
    content_category = models.CharField(max_length=50, blank=True)
    hashtags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PostMetrics(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='metrics')
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
```

#### 3. API Endpoints Implementation
```python
# apps/social/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Post, SocialMediaAccount
from .serializers import PostSerializer, SocialMediaAccountSerializer

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a post for later publishing"""
        post = self.get_object()
        scheduled_time = request.data.get('scheduled_at')
        
        if not scheduled_time:
            return Response(
                {'error': 'scheduled_at is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.scheduled_at = scheduled_time
        post.status = 'scheduled'
        post.save()
        
        # Add to Celery queue for publishing
        from .tasks import publish_scheduled_post
        publish_scheduled_post.apply_async(
            args=[post.id], 
            eta=post.scheduled_at
        )
        
        return Response({'message': 'Post scheduled successfully'})
    
    @action(detail=True, methods=['post'])
    def publish_now(self, request, pk=None):
        """Publish a post immediately"""
        post = self.get_object()
        
        # Call social media API to publish
        from .services import SocialMediaService
        service = SocialMediaService()
        
        try:
            result = service.publish_post(post)
            post.status = 'published'
            post.published_at = timezone.now()
            post.platform_post_id = result.get('post_id')
            post.save()
            
            return Response({'message': 'Post published successfully'})
        except Exception as e:
            post.status = 'failed'
            post.save()
            return Response(
                {'error': f'Failed to publish: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    serializer_class = SocialMediaAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialMediaAccount.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def connect_account(self, request):
        """Connect a new social media account"""
        platform = request.data.get('platform')
        access_token = request.data.get('access_token')
        
        if not platform or not access_token:
            return Response(
                {'error': 'platform and access_token are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify token and get user info from platform
        from .services import SocialMediaService
        service = SocialMediaService()
        
        try:
            user_info = service.verify_token(platform, access_token)
            
            account, created = SocialMediaAccount.objects.get_or_create(
                user=request.user,
                platform=platform,
                platform_user_id=user_info['user_id'],
                defaults={
                    'username': user_info['username'],
                    'access_token': access_token,
                    'followers_count': user_info.get('followers_count', 0),
                    'following_count': user_info.get('following_count', 0),
                }
            )
            
            if not created:
                # Update existing account
                account.access_token = access_token
                account.username = user_info['username']
                account.is_active = True
                account.save()
            
            return Response({
                'message': 'Account connected successfully',
                'account_id': account.id
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to connect account: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
```

#### 4. Background Tasks with Celery
```python
# apps/social/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Post
from .services import SocialMediaService
import logging

logger = logging.getLogger(__name__)

@shared_task
def publish_scheduled_post(post_id):
    """Publish a scheduled post"""
    try:
        post = Post.objects.get(id=post_id)
        
        if post.status != 'scheduled':
            logger.warning(f'Post {post_id} is not in scheduled status')
            return
        
        service = SocialMediaService()
        result = service.publish_post(post)
        
        post.status = 'published'
        post.published_at = timezone.now()
        post.platform_post_id = result.get('post_id')
        post.save()
        
        logger.info(f'Successfully published post {post_id}')
        
    except Post.DoesNotExist:
        logger.error(f'Post {post_id} not found')
    except Exception as e:
        logger.error(f'Failed to publish post {post_id}: {str(e)}')
        
        # Update post status to failed
        try:
            post = Post.objects.get(id=post_id)
            post.status = 'failed'
            post.save()
        except:
            pass

@shared_task
def sync_post_metrics():
    """Sync metrics for published posts"""
    from datetime import timedelta
    
    # Get posts published in the last 7 days
    cutoff_date = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(
        status='published',
        published_at__gte=cutoff_date
    ).select_related('social_account')
    
    service = SocialMediaService()
    
    for post in posts:
        try:
            metrics = service.get_post_metrics(post)
            
            # Update or create metrics
            from .models import PostMetrics
            PostMetrics.objects.update_or_create(
                post=post,
                defaults={
                    'likes_count': metrics.get('likes', 0),
                    'comments_count': metrics.get('comments', 0),
                    'shares_count': metrics.get('shares', 0),
                    'views_count': metrics.get('views', 0),
                    'engagement_rate': metrics.get('engagement_rate', 0.0),
                }
            )
            
        except Exception as e:
            logger.error(f'Failed to sync metrics for post {post.id}: {str(e)}')
```

### Development Tasks for Backend Team

#### Week 1-2: Foundation
- [ ] Set up Django project structure
- [ ] Configure database settings (PostgreSQL)
- [ ] Implement user authentication system
- [ ] Create basic API endpoints for user management
- [ ] Set up Celery for background tasks
- [ ] Configure Redis for caching

#### Week 3-4: Core Features
- [ ] Implement social media account connection
- [ ] Create post management API endpoints
- [ ] Build content scheduling system
- [ ] Integrate with social media APIs (Twitter, Facebook, etc.)
- [ ] Implement post publishing functionality

#### Week 5-6: Advanced Features
- [ ] Build analytics API endpoints
- [ ] Implement subscription and billing system
- [ ] Create webhook handlers for social media platforms
- [ ] Add post metrics synchronization
- [ ] Implement rate limiting and API throttling

#### Week 7-8: Optimization
- [ ] Performance optimization and caching
- [ ] API documentation with Swagger
- [ ] Error handling and logging improvements
- [ ] Security enhancements
- [ ] Production deployment preparation

---

## Frontend Team (React) Guide

### Overview
The frontend team builds the user interface using React 18, TypeScript, and modern web technologies to create an intuitive and responsive social media management dashboard.

### Project Structure
```
clientnest-frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── common/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── posts/
│   │   ├── analytics/
│   │   └── settings/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   ├── store/
│   ├── types/
│   ├── utils/
│   └── styles/
├── package.json
└── vite.config.ts
```

### Key Responsibilities

#### 1. Authentication Components
```tsx
// src/components/auth/LoginForm.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { authService } from '../../services/authService';

interface LoginFormData {
  email: string;
  password: string;
}

export const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.login(formData);
      login(response.user, response.token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-center mb-6">Sign In</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Password
          </label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
        >
          {isLoading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
};
```

#### 2. Dashboard Components
```tsx
// src/components/dashboard/DashboardOverview.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analyticsService';
import { MetricCard } from './MetricCard';
import { ChartContainer } from './ChartContainer';
import { RecentPosts } from './RecentPosts';
import { AIUsageWidget } from './AIUsageWidget';

export const DashboardOverview: React.FC = () => {
  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: analyticsService.getDashboardData,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Failed to load dashboard data. Please try again.
      </div>
    );
  }

  const { overview, content_performance, ai_usage, social_growth } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Posts"
          value={overview.total_posts}
          change={`+${overview.posts_this_week} this week`}
          icon="📝"
        />
        <MetricCard
          title="Social Accounts"
          value={overview.social_accounts}
          change="Connected platforms"
          icon="🔗"
        />
        <MetricCard
          title="Total Followers"
          value={overview.total_followers.toLocaleString()}
          change="Across all platforms"
          icon="👥"
        />
        <MetricCard
          title="AI Requests Today"
          value={overview.ai_requests_today}
          change="Content generated"
          icon="🤖"
        />
      </div>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartContainer
          title="Content Performance"
          data={content_performance}
          type="line"
        />
        <AIUsageWidget data={ai_usage} />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentPosts />
        </div>
        <div>
          <SocialGrowthWidget data={social_growth} />
        </div>
      </div>
    </div>
  );
};
```

#### 3. Post Management Components
```tsx
// src/components/posts/PostEditor.tsx
import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { postService } from '../../services/postService';
import { aiService } from '../../services/aiService';
import { MediaUploader } from './MediaUploader';
import { PlatformSelector } from './PlatformSelector';
import { ScheduleSelector } from './ScheduleSelector';

interface PostEditorProps {
  postId?: string;
  onSave?: () => void;
  onCancel?: () => void;
}

export const PostEditor: React.FC<PostEditorProps> = ({ 
  postId, 
  onSave, 
  onCancel 
}) => {
  const [content, setContent] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [mediaFiles, setMediaFiles] = useState<File[]>([]);
  const [scheduledAt, setScheduledAt] = useState<Date | null>(null);
  const [isGeneratingContent, setIsGeneratingContent] = useState(false);
  
  const queryClient = useQueryClient();

  const savePostMutation = useMutation({
    mutationFn: postService.createPost,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      onSave?.();
    },
  });

  const generateContentMutation = useMutation({
    mutationFn: aiService.generateContent,
    onSuccess: (generatedContent) => {
      setContent(generatedContent.content);
    },
  });

  const handleSave = async () => {
    const postData = {
      content,
      platforms: selectedPlatforms,
      media_files: mediaFiles,
      scheduled_at: scheduledAt,
    };

    savePostMutation.mutate(postData);
  };

  const handleGenerateContent = async () => {
    setIsGeneratingContent(true);
    try {
      await generateContentMutation.mutateAsync({
        prompt: content || 'Generate engaging social media content',
        platform: selectedPlatforms[0] || 'twitter',
        tone: 'professional',
      });
    } finally {
      setIsGeneratingContent(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="space-y-6">
        {/* Content Editor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content
          </label>
          <div className="relative">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="What's on your mind?"
              className="w-full h-32 p-3 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              maxLength={280}
            />
            <div className="absolute bottom-2 right-2 text-sm text-gray-500">
              {content.length}/280
            </div>
          </div>
          
          <button
            onClick={handleGenerateContent}
            disabled={isGeneratingContent}
            className="mt-2 px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 disabled:opacity-50"
          >
            {isGeneratingContent ? '🤖 Generating...' : '🤖 AI Generate'}
          </button>
        </div>

        {/* Platform Selection */}
        <PlatformSelector
          selected={selectedPlatforms}
          onChange={setSelectedPlatforms}
        />

        {/* Media Upload */}
        <MediaUploader
          files={mediaFiles}
          onChange={setMediaFiles}
        />

        {/* Schedule Options */}
        <ScheduleSelector
          scheduledAt={scheduledAt}
          onChange={setScheduledAt}
        />

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={() => handleSave()}
            disabled={!content.trim() || selectedPlatforms.length === 0}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
          >
            {scheduledAt ? 'Schedule Post' : 'Publish Now'}
          </button>
        </div>
      </div>
    </div>
  );
};
```

#### 4. State Management with Zustand
```tsx
// src/store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  username: string;
  subscription_tier: string;
  ai_tokens_used: number;
  ai_tokens_limit: number;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(n  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: (user, token) => {
        set({
          user,
          token,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      updateUser: (userData) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData },
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### Development Tasks for Frontend Team

#### Week 1-2: Foundation
- [ ] Set up React project with Vite and TypeScript
- [ ] Configure Tailwind CSS and component library
- [ ] Implement authentication pages (login, register, forgot password)
- [ ] Set up routing with React Router
- [ ] Create basic layout components (header, sidebar, footer)
- [ ] Implement state management with Zustand

#### Week 3-4: Core Features
- [ ] Build dashboard overview page
- [ ] Create post editor and management interface
- [ ] Implement social media account connection flow
- [ ] Build content calendar view
- [ ] Add post scheduling functionality
- [ ] Create responsive mobile layouts

#### Week 5-6: Advanced Features
- [ ] Implement analytics dashboard with charts
- [ ] Build AI content generation interface
- [ ] Add real-time notifications
- [ ] Create user settings and profile pages
- [ ] Implement dark mode toggle
- [ ] Add export functionality for reports

#### Week 7-8: Optimization
- [ ] Performance optimization and code splitting
- [ ] Accessibility improvements (WCAG compliance)
- [ ] Cross-browser testing and fixes
- [ ] Error boundary implementation
- [ ] Production build optimization
- [ ] User experience testing and refinements

---

## Data Science Team Guide

### Overview
The data science team focuses on building analytics, machine learning models, and data pipelines to provide insights and intelligent features for ClientNest users.

### Key Responsibilities

#### 1. Data Pipeline Development
```python
# data_science/pipelines/etl_pipeline.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from sqlalchemy import create_engine
import redis

class DataPipeline:
    def __init__(self, db_config: Dict, redis_config: Dict):
        self.db_engine = create_engine(db_config['url'])
        self.redis_client = redis.Redis(**redis_config)
        self.logger = logging.getLogger(__name__)
    
    def extract_user_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract user activity data from PostgreSQL"""
        query = """
        SELECT 
            u.id as user_id,
            u.subscription_tier,
            u.created_at as user_created_at,
            COUNT(p.id) as total_posts,
            AVG(pm.engagement_rate) as avg_engagement_rate,
            SUM(pm.likes_count + pm.comments_count + pm.shares_count) as total_engagement,
            COUNT(DISTINCT p.social_account_id) as active_platforms
        FROM users_user u
        LEFT JOIN social_post p ON u.id = p.user_id
        LEFT JOIN social_postmetrics pm ON p.id = pm.post_id
        WHERE p.created_at BETWEEN %s AND %s
        GROUP BY u.id, u.subscription_tier, u.created_at
        """
        
        return pd.read_sql(query, self.db_engine, params=[start_date, end_date])
    
    def extract_post_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract post performance data"""
        query = """
        SELECT 
            p.id as post_id,
            p.user_id,
            p.content,
            p.platform,
            p.ai_generated,
            p.content_category,
            p.created_at,
            p.published_at,
            pm.likes_count,
            pm.comments_count,
            pm.shares_count,
            pm.views_count,
            pm.engagement_rate,
            EXTRACT(hour FROM p.published_at) as publish_hour,
            EXTRACT(dow FROM p.published_at) as publish_day_of_week
        FROM social_post p
        LEFT JOIN social_postmetrics pm ON p.id = pm.post_id
        WHERE p.published_at BETWEEN %s AND %s
        AND p.status = 'published'
        """
        
        return pd.read_sql(query, self.db_engine, params=[start_date, end_date])
    
    def transform_engagement_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data to create engagement prediction features"""
        # Calculate engagement score
        df['engagement_score'] = (
            df['likes_count'] * 1.0 + 
            df['comments_count'] * 2.0 + 
            df['shares_count'] * 3.0
        )
        
        # Content length features
        df['content_length'] = df['content'].str.len()
        df['word_count'] = df['content'].str.split().str.len()
        df['hashtag_count'] = df['content'].str.count('#')
        df['mention_count'] = df['content'].str.count('@')
        df['url_count'] = df['content'].str.count('http')
        
        # Time-based features
        df['is_weekend'] = df['publish_day_of_week'].isin([0, 6])  # Sunday=0, Saturday=6
        df['is_business_hours'] = df['publish_hour'].between(9, 17)
        df['is_prime_time'] = df['publish_hour'].between(18, 22)
        
        # Platform-specific features
        platform_dummies = pd.get_dummies(df['platform'], prefix='platform')
        df = pd.concat([df, platform_dummies], axis=1)
        
        # Category features
        category_dummies = pd.get_dummies(df['content_category'], prefix='category')
        df = pd.concat([df, category_dummies], axis=1)
        
        return df
    
    def load_to_analytics_db(self, df: pd.DataFrame, table_name: str):
        """Load processed data to analytics database"""
        try:
            df.to_sql(table_name, self.db_engine, if_exists='append', index=False)
            self.logger.info(f"Successfully loaded {len(df)} records to {table_name}")
        except Exception as e:
            self.logger.error(f"Failed to load data to {table_name}: {str(e)}")
            raise
    
    def cache_aggregated_metrics(self, df: pd.DataFrame):
        """Cache aggregated metrics in Redis for fast access"""
        # Platform performance metrics
        platform_metrics = df.groupby('platform').agg({
            'engagement_score': ['mean', 'median', 'std'],
            'engagement_rate': ['mean', 'median'],
            'post_id': 'count'
        }).round(2)
        
        for platform in platform_metrics.index:
            metrics = platform_metrics.loc[platform].to_dict()
            self.redis_client.hset(
                f"platform_metrics:{platform}", 
                mapping=metrics
            )
            self.redis_client.expire(f"platform_metrics:{platform}", 3600)  # 1 hour TTL
        
        # Time-based performance metrics
        hourly_metrics = df.groupby('publish_hour')['engagement_score'].mean().to_dict()
        self.redis_client.hset("hourly_engagement", mapping=hourly_metrics)
        self.redis_client.expire("hourly_engagement", 3600)
        
        daily_metrics = df.groupby('publish_day_of_week')['engagement_score'].mean().to_dict()
        self.redis_client.hset("daily_engagement", mapping=daily_metrics)
        self.redis_client.expire("daily_engagement", 3600)
```

#### 2. Machine Learning Models
```python
# data_science/models/engagement_predictor.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from typing import Dict, List, Tuple

class EngagementPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.is_trained = False
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for model training"""
        feature_columns = [
            'content_length', 'word_count', 'hashtag_count', 'mention_count', 'url_count',
            'publish_hour', 'publish_day_of_week', 'is_weekend', 'is_business_hours', 'is_prime_time',
            'ai_generated'
        ]
        
        # Add platform dummy variables
        platform_columns = [col for col in df.columns if col.startswith('platform_')]
        feature_columns.extend(platform_columns)
        
        # Add category dummy variables
        category_columns = [col for col in df.columns if col.startswith('category_')]
        feature_columns.extend(category_columns)
        
        # Store feature columns for later use
        self.feature_columns = feature_columns
        
        return df[feature_columns].fillna(0)
    
    def train(self, df: pd.DataFrame, target_column: str = 'engagement_score') -> Dict:
        """Train the engagement prediction model"""
        # Prepare features and target
        X = self.prepare_features(df)
        y = df[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='r2')
        
        self.is_trained = True
        
        return {
            'mse': mse,
            'r2': r2,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
        }
    
    def predict(self, content: str, platform: str, publish_time: datetime, 
                user_features: Dict = None) -> Dict:
        """Predict engagement for a piece of content"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Create feature vector
        features = self._extract_content_features(content)
        features.update(self._extract_time_features(publish_time))
        features.update(self._extract_platform_features(platform))
        
        if user_features:
            features.update(user_features)
        
        # Convert to DataFrame with correct column order
        feature_df = pd.DataFrame([features])
        feature_df = feature_df.reindex(columns=self.feature_columns, fill_value=0)
        
        # Scale and predict
        features_scaled = self.scaler.transform(feature_df)
        prediction = self.model.predict(features_scaled)[0]
        
        # Get prediction confidence (using feature importance)
        confidence = self._calculate_confidence(features)
        
        return {
            'predicted_engagement': max(0, prediction),  # Ensure non-negative
            'confidence': confidence,
            'recommendation': self._get_recommendation(prediction)
        }
    
    def _extract_content_features(self, content: str) -> Dict:
        """Extract features from content text"""
        return {
            'content_length': len(content),
            'word_count': len(content.split()),
            'hashtag_count': content.count('#'),
            'mention_count': content.count('@'),
            'url_count': content.count('http'),
            'ai_generated': 0  # Default to human-generated
        }
    
    def _extract_time_features(self, publish_time: datetime) -> Dict:
        """Extract time-based features"""
        return {
            'publish_hour': publish_time.hour,
            'publish_day_of_week': publish_time.weekday(),
            'is_weekend': publish_time.weekday() >= 5,
            'is_business_hours': 9 <= publish_time.hour <= 17,
            'is_prime_time': 18 <= publish_time.hour <= 22
        }
    
    def _extract_platform_features(self, platform: str) -> Dict:
        """Extract platform-specific features"""
        platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'tiktok']
        features = {f'platform_{p}': 0 for p in platforms}
        if f'platform_{platform}' in features:
            features[f'platform_{platform}'] = 1
        return features
    
    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate prediction confidence based on feature quality"""
        # Simple confidence calculation based on feature completeness
        total_features = len(self.feature_columns)
        non_zero_features = sum(1 for v in features.values() if v != 0)
        return min(0.95, non_zero_features / total_features)
    
    def _get_recommendation(self, prediction: float) -> str:
        """Get recommendation based on prediction"""
        if prediction > 100:
            return "Excellent! This content is predicted to perform very well."
        elif prediction > 50:
            return "Good potential. Consider optimizing posting time for better reach."
        elif prediction > 20:
            return "Moderate performance expected. Try adding more engaging elements."
        else:
            return "Low engagement predicted. Consider revising content or trying a different approach."
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
```

### Development Tasks for Data Science Team

#### Week 1-2: Data Infrastructure
- [ ] Set up data pipeline infrastructure
- [ ] Create ETL processes for user and post data
- [ ] Implement data quality checks and validation
- [ ] Set up analytics database schema
- [ ] Create data monitoring and alerting

#### Week 3-4: Analytics Development
- [ ] Build user analytics API endpoints
- [ ] Implement real-time dashboard data processing
- [ ] Create engagement prediction models
- [ ] Develop content performance analytics
- [ ] Set up A/B testing framework

#### Week 5-6: Machine Learning Models
- [ ] Implement churn prediction models
- [ ] Build content recommendation system
- [ ] Create optimal timing analysis
- [ ] Develop sentiment analysis for comments
- [ ] Implement model evaluation and monitoring

#### Week 7-8: Advanced Analytics
- [ ] Build advanced reporting features
- [ ] Implement predictive analytics dashboard
- [ ] Create automated insights generation
- [ ] Optimize model performance and accuracy
- [ ] Deploy models to production

---

## AI Team Guide

### Overview
The AI team integrates DeepSeek API and other AI services to provide content generation, optimization, and intelligent features throughout the ClientNest platform.

### Key Responsibilities

#### 1. AI Service Integration
```python
# ai/services/deepseek_client.py
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

@dataclass
class AIRequest:
    prompt: str
    model: str = "deepseek-chat"
    max_tokens: int = 1000
    temperature: float = 0.7
    platform: str = "general"
    content_type: str = "post"

@dataclass
class AIResponse:
    content: str
    tokens_used: int
    cost: float
    model: str
    request_id: str
    created_at: datetime

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_content(self, request: AIRequest) -> AIResponse:
        """Generate content using DeepSeek API"""
        
        # Prepare the request payload
        payload = {
            "model": request.model,
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt(request.platform, request.content_type)
                },
                {
                    "role": "user",
                    "content": request.prompt
                }
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API request failed: {response.status} - {error_text}")
                
                data = await response.json()
                
                # Extract response data
                content = data["choices"][0]["message"]["content"]
                tokens_used = data["usage"]["total_tokens"]
                
                # Calculate cost (example pricing)
                cost = self._calculate_cost(tokens_used, request.model)
                
                return AIResponse(
                    content=content.strip(),
                    tokens_used=tokens_used,
                    cost=cost,
                    model=request.model,
                    request_id=data.get("id", ""),
                    created_at=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"DeepSeek API error: {str(e)}")
            raise
    
    def _get_system_prompt(self, platform: str, content_type: str) -> str:
        """Get platform-specific system prompt"""
        
        base_prompt = "You are a professional social media content creator."
        
        platform_prompts = {
            "twitter": "Create engaging Twitter content. Keep it concise, use relevant hashtags, and make it shareable. Maximum 280 characters.",
            "facebook": "Create engaging Facebook content. Use a conversational tone, encourage interaction, and include relevant hashtags.",
            "instagram": "Create visually appealing Instagram content. Use engaging captions, relevant hashtags, and encourage user interaction.",
            "linkedin": "Create professional LinkedIn content. Use a business tone, provide value, and encourage professional networking.",
            "tiktok": "Create trendy TikTok content. Use current trends, engaging hooks, and popular hashtags."
        }
        
        content_type_prompts = {
            "post": "Focus on creating engaging social media posts.",
            "comment": "Focus on creating thoughtful, engaging comments that add value to the conversation.",
            "caption": "Focus on creating compelling captions that complement visual content.",
            "hashtags": "Focus on generating relevant, trending hashtags."
        }
        
        platform_specific = platform_prompts.get(platform, "Create engaging social media content.")
        content_specific = content_type_prompts.get(content_type, "")
        
        return f"{base_prompt} {platform_specific} {content_specific}"
    
    def _calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost based on token usage"""
        # Example pricing (adjust based on actual DeepSeek pricing)
        pricing = {
            "deepseek-chat": 0.0001,  # $0.0001 per token
            "deepseek-coder": 0.0001,
        }
        
        rate = pricing.get(model, 0.0001)
        return tokens * rate

class AIContentService:
    def __init__(self, deepseek_client: DeepSeekClient):
        self.client = deepseek_client
        self.logger = logging.getLogger(__name__)
    
    async def generate_post_content(self, 
                                  prompt: str, 
                                  platform: str, 
                                  tone: str = "professional",
                                  include_hashtags: bool = True) -> Dict[str, Any]:
        """Generate social media post content"""
        
        # Enhance prompt with tone and platform requirements
        enhanced_prompt = f"""
        Create a {tone} social media post for {platform} based on this topic: {prompt}
        
        Requirements:
        - Make it engaging and shareable
        - Use appropriate tone: {tone}
        - Optimize for {platform} best practices
        {'- Include relevant hashtags' if include_hashtags else '- Do not include hashtags'}
        - Keep within platform character limits
        """
        
        request = AIRequest(
            prompt=enhanced_prompt,
            platform=platform,
            content_type="post",
            temperature=0.7
        )
        
        try:
            response = await self.client.generate_content(request)
            
            # Extract hashtags if present
            content = response.content
            hashtags = self._extract_hashtags(content)
            
            return {
                "content": content,
                "hashtags": hashtags,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "platform": platform,
                "tone": tone
            }
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {str(e)}")
            raise
    
    async def optimize_content(self, 
                             content: str, 
                             platform: str, 
                             optimization_goals: List[str]) -> Dict[str, Any]:
        """Optimize existing content for better performance"""
        
        goals_text = ", ".join(optimization_goals)
        
        prompt = f"""
        Optimize this social media content for {platform}:
        
        Original content: {content}
        
        Optimization goals: {goals_text}
        
        Please provide:
        1. Optimized version of the content
        2. Explanation of changes made
        3. Expected improvements
        
        Keep the core message but improve engagement potential.
        """
        
        request = AIRequest(
            prompt=prompt,
            platform=platform,
            content_type="optimization",
            temperature=0.5  # Lower temperature for optimization
        )
        
        try:
            response = await self.client.generate_content(request)
            
            # Parse the response to extract optimized content and explanation
            optimized_data = self._parse_optimization_response(response.content)
            
            return {
                "original_content": content,
                "optimized_content": optimized_data.get("optimized_content", response.content),
                "explanation": optimized_data.get("explanation", ""),
                "expected_improvements": optimized_data.get("improvements", []),
                "tokens_used": response.tokens_used,
                "cost": response.cost
            }
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            raise
    
    async def generate_comment_responses(self, 
                                       original_post: str, 
                                       comments: List[str], 
                                       response_tone: str = "friendly") -> List[Dict[str, Any]]:
        """Generate responses to comments"""
        
        responses = []
        
        for comment in comments:
            prompt = f"""
            Generate a {response_tone} response to this comment on the following post:
            
            Original post: {original_post}
            Comment: {comment}
            
            Requirements:
            - Be {response_tone} and engaging
            - Add value to the conversation
            - Encourage further interaction
            - Keep it concise
            - Be authentic and human-like
            """
            
            request = AIRequest(
                prompt=prompt,
                content_type="comment",
                temperature=0.8,  # Higher temperature for more natural responses
                max_tokens=200  # Shorter responses for comments
            )
            
            try:
                response = await self.client.generate_content(request)
                
                responses.append({
                    "original_comment": comment,
                    "suggested_response": response.content,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost
                })
                
            except Exception as e:
                self.logger.error(f"Comment response generation failed: {str(e)}")
                responses.append({
                    "original_comment": comment,
                    "error": str(e)
                })
        
        return responses
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        import re
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, content)
        return [tag.lower() for tag in hashtags]
    
    def _parse_optimization_response(self, response: str) -> Dict[str, Any]:
        """Parse optimization response to extract structured data"""
        # Simple parsing logic - in production, you might want more sophisticated parsing
        lines = response.split('\n')
        
        result = {
            "optimized_content": "",
            "explanation": "",
            "improvements": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "optimized" in line.lower() and ":" in line:
                current_section = "optimized_content"
                continue
            elif "explanation" in line.lower() and ":" in line:
                current_section = "explanation"
                continue
            elif "improvement" in line.lower() and ":" in line:
                current_section = "improvements"
                continue
            
            if current_section == "optimized_content":
                result["optimized_content"] += line + " "
            elif current_section == "explanation":
                result["explanation"] += line + " "
            elif current_section == "improvements":
                if line.startswith("-") or line.startswith("•"):
                    result["improvements"].append(line[1:].strip())
        
        # Clean up
        result["optimized_content"] = result["optimized_content"].strip()
        result["explanation"] = result["explanation"].strip()
        
        return result
```

### Development Tasks for AI Team

#### Week 1-2: AI Infrastructure
- [ ] Set up DeepSeek API integration
- [ ] Implement AI client with rate limiting and error handling
- [ ] Create AI usage tracking and cost management
- [ ] Set up prompt templates and optimization
- [ ] Implement AI request queue system

#### Week 3-4: Content Generation
- [ ] Build content generation API endpoints
- [ ] Implement platform-specific content optimization
- [ ] Create hashtag generation and suggestion system
- [ ] Build content scheduling with AI optimization
- [ ] Implement A/B testing for AI-generated content

#### Week 5-6: Advanced AI Features
- [ ] Build comment management and response generation
- [ ] Implement sentiment analysis for user feedback
- [ ] Create content performance prediction
- [ ] Build personalized content recommendations
- [ ] Implement AI-powered content calendar optimization

#### Week 7-8: AI Optimization
- [ ] Optimize AI model performance and accuracy
- [ ] Implement advanced prompt engineering
- [ ] Build AI analytics and insights dashboard
- [ ] Create automated content quality scoring
- [ ] Deploy AI services to production with monitoring

---

## Security Team Guide

### Overview
The security team ensures ClientNest is secure, compliant, and protected against threats across all layers of the application.

### Key Responsibilities

#### 1. Authentication & Authorization
```python
# security/auth/jwt_handler.py
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from django.conf import settings
from django.contrib.auth import get_user_model
import redis

User = get_user_model()

class JWTHandler:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = 'HS256'
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=7)
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
    
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'subscription_tier': user.subscription_tier,
            'iat': now,
            'exp': now + self.access_token_expire,
            'type': 'access'
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user.id,
            'iat': now,
            'exp': now + self.refresh_token_expire,
            'type': 'refresh'
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token in Redis
        self.redis_client.setex(
            f"refresh_token:{user.id}",
            self.refresh_token_expire,
            refresh_token
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(self.access_token_expire.total_seconds())
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token using refresh token"""
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return None
        
        user_id = payload['user_id']
        
        # Verify refresh token exists in Redis
        stored_token = self.redis_client.get(f"refresh_token:{user_id}")
        if not stored_token or stored_token.decode() != refresh_token:
            return None
        
        try:
            user = User.objects.get(id=user_id)
            return self.generate_tokens(user)
        except User.DoesNotExist:
            return None
    
    def blacklist_token(self, token: str):
        """Add token to blacklist"""
        payload = self.verify_token(token)
        if payload:
            exp = payload['exp']
            ttl = exp - datetime.utcnow().timestamp()
            if ttl > 0:
                self.redis_client.setex(f"blacklist:{token}", int(ttl), "1")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return self.redis_client.exists(f"blacklist:{token}")
    
    def revoke_all_tokens(self, user_id: int):
        """Revoke all tokens for a user"""
        self.redis_client.delete(f"refresh_token:{user_id}")
```

#### 2. Input Validation & Sanitization
```python
# security/validators.py
import re
from typing import Any, Dict, List, Optional
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import bleach

class SecurityValidator:
    
    # Allowed HTML tags for content
    ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'a', 'br', 'p']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    
    @staticmethod
    def validate_email_address(email: str) -> str:
        """Validate and sanitize email address"""
        try:
            validate_email(email)
            return email.lower().strip()
        except ValidationError:
            raise ValidationError("Invalid email address format")
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character")
        
        return True
    
    @staticmethod
    def sanitize_content(content: str) -> str:
        """Sanitize user-generated content"""
        # Remove potentially dangerous HTML
        cleaned = bleach.clean(
            content,
            tags=SecurityValidator.ALLOWED_TAGS,
            attributes=SecurityValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        # Additional sanitization
        cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'vbscript:', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'onload', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    @staticmethod
    def validate_social_media_token(token: str, platform: str) -> bool:
        """Validate social media access token format"""
        if not token or len(token) < 10:
            return False
        
        # Platform-specific validation
        platform_patterns = {
            'twitter': r'^[A-Za-z0-9_-]+$',
            'facebook': r'^[A-Za-z0-9_-]+$',
            'instagram': r'^[A-Za-z0-9_.-]+$',
            'linkedin': r'^[A-Za-z0-9_-]+$'
        }
        
        pattern = platform_patterns.get(platform)
        if pattern and not re.match(pattern, token):
            return False
        
        return True
    
    @staticmethod
    def validate_api_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize API request data"""
        validated_data = {}
        
        for key, value in data.items():
            # Sanitize key names
            clean_key = re.sub(r'[^a-zA-Z0-9_]', '', key)
            
            if isinstance(value, str):
                # Sanitize string values
                validated_data[clean_key] = SecurityValidator.sanitize_content(value)
            elif isinstance(value, (int, float, bool)):
                validated_data[clean_key] = value
            elif isinstance(value, list):
                # Sanitize list items
                validated_data[clean_key] = [
                    SecurityValidator.sanitize_content(item) if isinstance(item, str) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                # Recursively validate nested objects
                validated_data[clean_key] = SecurityValidator.validate_api_request(value)
        
        return validated_data
```

### Development Tasks for Security Team

#### Week 1-2: Authentication & Authorization
- [ ] Implement JWT-based authentication system
- [ ] Set up role-based access control (RBAC)
- [ ] Create secure password hashing and validation
- [ ] Implement multi-factor authentication (MFA)
- [ ] Set up session management and token blacklisting

#### Week 3-4: Data Protection
- [ ] Implement input validation and sanitization
- [ ] Set up database encryption at rest
- [ ] Create secure API endpoints with rate limiting
- [ ] Implement CORS and security headers
- [ ] Set up audit logging for sensitive operations

#### Week 5-6: Infrastructure Security
- [ ] Configure AWS security groups and IAM policies
- [ ] Set up SSL/TLS certificates and HTTPS enforcement
- [ ] Implement security monitoring and alerting
- [ ] Create backup and disaster recovery procedures
- [ ] Set up vulnerability scanning and penetration testing

#### Week 7-8: Compliance & Monitoring
- [ ] Implement GDPR compliance features
- [ ] Set up security incident response procedures
- [ ] Create security documentation and training
- [ ] Implement continuous security monitoring
- [ ] Conduct security audit and penetration testing

---

## Cross-Team Collaboration

### Communication Protocols

#### Daily Standups
- **Time**: 9:00 AM daily
- **Duration**: 15 minutes
- **Format**: Each team reports progress, blockers, and dependencies

#### Weekly Architecture Reviews
- **Time**: Fridays 2:00 PM
- **Duration**: 1 hour
- **Participants**: Team leads + Architecture team
- **Purpose**: Review technical decisions and ensure alignment

#### Sprint Planning
- **Time**: Every 2 weeks, Mondays 10:00 AM
- **Duration**: 2 hours
- **Purpose**: Plan upcoming sprint tasks and dependencies

### Integration Points

#### Backend ↔ Frontend
- **API Contract**: RESTful APIs with OpenAPI documentation
- **Authentication**: JWT tokens with role-based access
- **Data Format**: JSON with consistent error handling
- **Testing**: Contract testing with Pact

#### Backend ↔ Data Science
- **Data Pipeline**: Scheduled ETL jobs with error handling
- **Model Integration**: REST API endpoints for ML predictions
- **Monitoring**: Shared metrics and alerting

#### Backend ↔ AI
- **Service Integration**: Async queue-based processing
- **Cost Management**: Shared usage tracking and limits
- **Error Handling**: Graceful degradation when AI services fail

#### All Teams ↔ Security
- **Code Reviews**: Security team reviews all PRs
- **Vulnerability Scanning**: Automated security checks in CI/CD
- **Incident Response**: Shared security incident procedures

### Development Workflow

#### Git Workflow
1. **Feature Branches**: `feature/team-name/feature-description`
2. **Pull Requests**: Required for all changes
3. **Code Reviews**: Minimum 2 approvals (including security for sensitive changes)
4. **Testing**: All tests must pass before merge
5. **Deployment**: Automated deployment to staging, manual to production

#### Environment Management
- **Development**: Local development with Docker
- **Staging**: Shared staging environment for integration testing
- **Production**: Blue-green deployment with rollback capability

### Success Metrics

#### Technical Metrics
- **API Response Time**: < 200ms for 95% of requests
- **System Uptime**: 99.9% availability
- **Security Incidents**: Zero critical security vulnerabilities
- **Code Coverage**: > 80% test coverage

#### Team Metrics
- **Sprint Velocity**: Consistent story point completion
- **Bug Rate**: < 5% of features require hotfixes
- **Code Review Time**: < 24 hours average review time
- **Documentation**: 100% of APIs documented

### Tools & Resources

#### Development Tools
- **IDE**: VS Code with team extensions
- **Version Control**: Git with GitHub
- **Project Management**: Jira or Linear
- **Communication**: Slack with team channels

#### Monitoring & Observability
- **Application Monitoring**: New Relic or DataDog
- **Log Management**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Error Tracking**: Sentry
- **Performance Monitoring**: Grafana + Prometheus

#### Documentation
- **API Documentation**: Swagger/OpenAPI
- **Architecture Documentation**: This repository
- **Team Documentation**: Confluence or Notion
- **Code Documentation**: Inline comments + README files

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
- Set up development environments
- Implement basic authentication
- Create database schema
- Set up CI/CD pipelines
- Establish team communication protocols

### Phase 2: Core Features (Weeks 3-4)
- Build user management system
- Implement social media integration
- Create basic post management
- Set up AI service integration
- Implement basic security measures

### Phase 3: Advanced Features (Weeks 5-6)
- Build analytics dashboard
- Implement AI content generation
- Create advanced scheduling
- Add real-time features
- Implement comprehensive monitoring

### Phase 4: Optimization & Launch (Weeks 7-8)
- Performance optimization
- Security hardening
- User acceptance testing
- Production deployment
- Launch preparation

---

## Conclusion

This comprehensive guide provides each team with the specific knowledge and tasks needed to successfully build ClientNest. The modular architecture ensures that teams can work independently while maintaining system coherence through well-defined interfaces and communication protocols.

Remember to:
- Follow the established coding standards and patterns
- Communicate early and often about dependencies
- Prioritize security and performance from the start
- Document your work for future team members
- Test thoroughly at every level

Good luck building an amazing social media management platform! 🚀