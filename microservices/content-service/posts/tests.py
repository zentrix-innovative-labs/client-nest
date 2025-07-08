from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import timedelta
import json

from .models import (
    SocialAccount,
    Post,
    PostMedia,
    PostPlatform,
    Comment,
    PostStatus,
    SocialPlatform,
    PostType
)
from .tasks import publish_post_task, schedule_post_task

User = get_user_model()

class SocialAccountModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_social_account_creation(self):
        """Test creating a social media account"""
        account = SocialAccount.objects.create(
            user=self.user,
            platform=SocialPlatform.FACEBOOK,
            platform_username='testuser',
            platform_user_id='123456789',
            access_token='test_token',
            is_active=True
        )
        
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.platform, SocialPlatform.FACEBOOK)
        self.assertEqual(account.platform_username, 'testuser')
        self.assertTrue(account.is_active)
    
    def test_social_account_str(self):
        """Test string representation of social account"""
        account = SocialAccount.objects.create(
            user=self.user,
            platform=SocialPlatform.TWITTER,
            platform_username='testuser'
        )
        
        expected = f"{SocialPlatform.TWITTER} - testuser"
        self.assertEqual(str(account), expected)

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.social_account = SocialAccount.objects.create(
            user=self.user,
            platform=SocialPlatform.FACEBOOK,
            platform_username='testuser',
            is_active=True
        )
    
    def test_post_creation(self):
        """Test creating a post"""
        post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='This is a test post content',
            type=PostType.TEXT,
            status=PostStatus.DRAFT
        )
        
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.status, PostStatus.DRAFT)
        self.assertEqual(post.type, PostType.TEXT)
    
    def test_post_str(self):
        """Test string representation of post"""
        post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content'
        )
        
        self.assertEqual(str(post), 'Test Post')
    
    def test_scheduled_post(self):
        """Test creating a scheduled post"""
        future_time = timezone.now() + timedelta(hours=1)
        post = Post.objects.create(
            user=self.user,
            title='Scheduled Post',
            content='This will be published later',
            status=PostStatus.SCHEDULED,
            scheduled_at=future_time
        )
        
        self.assertEqual(post.status, PostStatus.SCHEDULED)
        self.assertIsNotNone(post.scheduled_at)
        self.assertTrue(post.scheduled_at > timezone.now())

class PostPlatformModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.social_account = SocialAccount.objects.create(
            user=self.user,
            platform=SocialPlatform.FACEBOOK,
            platform_username='testuser',
            is_active=True
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content'
        )
    
    def test_post_platform_creation(self):
        """Test creating a post platform relationship"""
        post_platform = PostPlatform.objects.create(
            post=self.post,
            social_account=self.social_account,
            status=PostStatus.DRAFT
        )
        
        self.assertEqual(post_platform.post, self.post)
        self.assertEqual(post_platform.social_account, self.social_account)
        self.assertEqual(post_platform.status, PostStatus.DRAFT)
    
    def test_post_platform_str(self):
        """Test string representation of post platform"""
        post_platform = PostPlatform.objects.create(
            post=self.post,
            social_account=self.social_account
        )
        
        expected = f"{self.post.title} - {self.social_account.platform}"
        self.assertEqual(str(post_platform), expected)

class PostAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.social_account = SocialAccount.objects.create(
            user=self.user,
            platform=SocialPlatform.FACEBOOK,
            platform_username='testuser',
            is_active=True
        )
    
    def test_create_post(self):
        """Test creating a post via API"""
        url = reverse('posts:post-list')
        data = {
            'title': 'API Test Post',
            'content': 'This is a test post created via API',
            'type': PostType.TEXT,
            'platforms': [str(self.social_account.id)]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        
        post = Post.objects.first()
        self.assertEqual(post.title, 'API Test Post')
        self.assertEqual(post.user, self.user)
    
    def test_list_posts(self):
        """Test listing posts via API"""
        # Create test posts
        Post.objects.create(
            user=self.user,
            title='Post 1',
            content='Content 1'
        )
        Post.objects.create(
            user=self.user,
            title='Post 2',
            content='Content 2'
        )
        
        url = reverse('posts:post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_post(self):
        """Test retrieving a specific post via API"""
        post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content'
        )
        
        url = reverse('posts:post-detail', kwargs={'pk': post.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
    
    def test_update_post(self):
        """Test updating a post via API"""
        post = Post.objects.create(
            user=self.user,
            title='Original Title',
            content='Original content',
            status=PostStatus.DRAFT
        )
        
        url = reverse('posts:post-detail', kwargs={'pk': post.id})
        data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        post.refresh_from_db()
        self.assertEqual(post.title, 'Updated Title')
        self.assertEqual(post.content, 'Updated content')
    
    def test_delete_post(self):
        """Test deleting a post via API"""
        post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content'
        )
        
        url = reverse('posts:post-detail', kwargs={'pk': post.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
    
    @patch('posts.tasks.publish_post_task.delay')
    def test_publish_post(self, mock_publish_task):
        """Test publishing a post via API"""
        post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content',
            status=PostStatus.DRAFT
        )
        
        PostPlatform.objects.create(
            post=post,
            social_account=self.social_account
        )
        
        url = reverse('posts:post-publish', kwargs={'pk': post.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.PUBLISHED)
        mock_publish_task.assert_called_once_with(str(post.id))
    
    def test_schedule_post(self):
        """Test scheduling a post via API"""
        post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content',
            status=PostStatus.DRAFT
        )
        
        future_time = timezone.now() + timedelta(hours=1)
        url = reverse('posts:post-schedule', kwargs={'pk': post.id})
        data = {
            'scheduled_at': future_time.isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.SCHEDULED)
        self.assertIsNotNone(post.scheduled_at)
    
    def test_duplicate_post(self):
        """Test duplicating a post via API"""
        original_post = Post.objects.create(
            user=self.user,
            title='Original Post',
            content='Original content'
        )
        
        url = reverse('posts:post-duplicate', kwargs={'pk': original_post.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        
        duplicated_post = Post.objects.exclude(id=original_post.id).first()
        self.assertEqual(duplicated_post.title, 'Original Post (Copy)')
        self.assertEqual(duplicated_post.content, 'Original content')
        self.assertEqual(duplicated_post.status, PostStatus.DRAFT)

class PostTaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.social_account = SocialAccount.objects.create(
            user=self.user,
            platform=SocialPlatform.FACEBOOK,
            platform_username='testuser',
            is_active=True
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content'
        )
        self.post_platform = PostPlatform.objects.create(
            post=self.post,
            social_account=self.social_account
        )
    
    @patch('posts.tasks.publish_to_platform')
    def test_publish_post_task_success(self, mock_publish):
        """Test successful post publishing task"""
        mock_publish.return_value = {
            'success': True,
            'platform_post_id': 'fb_123',
            'platform_url': 'https://facebook.com/posts/fb_123'
        }
        
        result = publish_post_task(str(self.post.id))
        
        self.assertEqual(result['success_count'], 1)
        self.assertEqual(result['total_platforms'], 1)
        
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, PostStatus.PUBLISHED)
        
        self.post_platform.refresh_from_db()
        self.assertEqual(self.post_platform.status, PostStatus.PUBLISHED)
        self.assertEqual(self.post_platform.platform_post_id, 'fb_123')
    
    @patch('posts.tasks.publish_to_platform')
    def test_publish_post_task_failure(self, mock_publish):
        """Test failed post publishing task"""
        mock_publish.return_value = {
            'success': False,
            'error': 'API rate limit exceeded'
        }
        
        result = publish_post_task(str(self.post.id))
        
        self.assertEqual(result['success_count'], 0)
        self.assertEqual(result['total_platforms'], 1)
        
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, PostStatus.FAILED)
        
        self.post_platform.refresh_from_db()
        self.assertEqual(self.post_platform.status, PostStatus.FAILED)
        self.assertEqual(self.post_platform.error_message, 'API rate limit exceeded')
    
    def test_schedule_post_task(self):
        """Test scheduled post task"""
        # Set post as scheduled
        self.post.status = PostStatus.SCHEDULED
        self.post.scheduled_at = timezone.now() - timedelta(minutes=1)  # Past time
        self.post.save()
        
        with patch('posts.tasks.publish_post_task.delay') as mock_publish:
            schedule_post_task(str(self.post.id))
            
            self.post.refresh_from_db()
            self.assertEqual(self.post.status, PostStatus.PUBLISHED)
            mock_publish.assert_called_once_with(str(self.post.id))

class PostPermissionTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        self.post = Post.objects.create(
            user=self.user1,
            title='User 1 Post',
            content='Content by user 1'
        )
    
    def test_owner_can_access_post(self):
        """Test that post owner can access their post"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('posts:post-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_non_owner_cannot_access_post(self):
        """Test that non-owner cannot access post"""
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('posts:post-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unauthenticated_cannot_access_post(self):
        """Test that unauthenticated users cannot access posts"""
        url = reverse('posts:post-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PostFilterTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test posts
        self.draft_post = Post.objects.create(
            user=self.user,
            title='Draft Post',
            content='Draft content',
            status=PostStatus.DRAFT
        )
        
        self.published_post = Post.objects.create(
            user=self.user,
            title='Published Post',
            content='Published content',
            status=PostStatus.PUBLISHED,
            published_at=timezone.now()
        )
        
        self.scheduled_post = Post.objects.create(
            user=self.user,
            title='Scheduled Post',
            content='Scheduled content',
            status=PostStatus.SCHEDULED,
            scheduled_at=timezone.now() + timedelta(hours=1)
        )
    
    def test_filter_by_status(self):
        """Test filtering posts by status"""
        url = reverse('posts:post-list')
        
        # Filter by draft status
        response = self.client.get(url, {'status': PostStatus.DRAFT})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Draft Post')
        
        # Filter by published status
        response = self.client.get(url, {'status': PostStatus.PUBLISHED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Published Post')
    
    def test_search_posts(self):
        """Test searching posts by content"""
        url = reverse('posts:post-list')
        
        response = self.client.get(url, {'search': 'Draft'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Draft Post')
    
    def test_filter_by_date_range(self):
        """Test filtering posts by date range"""
        url = reverse('posts:post-list')
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        response = self.client.get(url, {
            'created_after': today.isoformat(),
            'created_before': tomorrow.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All posts should be included as they were created today
        self.assertEqual(len(response.data['results']), 3)