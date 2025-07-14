from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Post, Schedule, Comment, CommentLike
from .serializers import PostSerializer, ScheduleSerializer

User = get_user_model()


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='This is a test post content',
            status='draft'
        )

    def test_post_creation(self):
        """Test that a post can be created successfully"""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post content')
        self.assertEqual(self.post.status, 'draft')
        self.assertEqual(self.post.user, self.user)

    def test_post_str_representation(self):
        """Test the string representation of a post"""
        expected_str = f"{self.post.title} - {self.post.status}"
        self.assertEqual(str(self.post), expected_str)

    def test_post_ordering(self):
        """Test that posts are ordered by created_at in descending order"""
        post2 = Post.objects.create(
            user=self.user,
            title='Second Post',
            content='Second post content',
            status='published'
        )
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)  # Newer post should come first
        self.assertEqual(posts[1], self.post)

    def test_post_status_choices(self):
        """Test that post status choices are valid"""
        valid_statuses = ['draft', 'scheduled', 'published', 'failed']
        for status in valid_statuses:
            post = Post.objects.create(
                user=self.user,
                title=f'Post with {status} status',
                content='Content',
                status=status
            )
            self.assertEqual(post.status, status)


class ScheduleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='This is a test post content',
            status='draft'
        )
        self.scheduled_time = timezone.now() + timedelta(hours=1)
        self.schedule = Schedule.objects.create(
            post=self.post,
            platform='facebook',
            scheduled_time=self.scheduled_time
        )

    def test_schedule_creation(self):
        """Test that a schedule can be created successfully"""
        self.assertEqual(self.schedule.post, self.post)
        self.assertEqual(self.schedule.platform, 'facebook')
        self.assertEqual(self.schedule.scheduled_time, self.scheduled_time)
        self.assertFalse(self.schedule.is_published)

    def test_schedule_str_representation(self):
        """Test the string representation of a schedule"""
        expected_str = f"{self.post.title} - facebook - {self.scheduled_time}"
        self.assertEqual(str(self.schedule), expected_str)

    def test_schedule_ordering(self):
        """Test that schedules are ordered by scheduled_time"""
        schedule2 = Schedule.objects.create(
            post=self.post,
            platform='instagram',
            scheduled_time=self.scheduled_time + timedelta(hours=2)
        )
        schedules = Schedule.objects.all()
        self.assertEqual(schedules[0], self.schedule)  # Earlier time should come first
        self.assertEqual(schedules[1], schedule2)


class PostSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='This is a test post content',
            status='draft',
            media_url='https://example.com/image.jpg'
        )
        self.schedule = Schedule.objects.create(
            post=self.post,
            platform='facebook',
            scheduled_time=timezone.now() + timedelta(hours=1)
        )

    def test_post_serializer_fields(self):
        """Test that PostSerializer includes all required fields"""
        serializer = PostSerializer(self.post)
        data = serializer.data
        
        expected_fields = [
            'id', 'user', 'title', 'content', 'media_url', 'status',
            'created_at', 'updated_at', 'published_at', 'schedules'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)

    def test_post_serializer_read_only_fields(self):
        """Test that read-only fields are properly handled"""
        serializer = PostSerializer(self.post)
        data = serializer.data
        
        # These fields should be present but not writable
        read_only_fields = ['created_at', 'updated_at', 'published_at']
        for field in read_only_fields:
            self.assertIn(field, data)

    def test_post_serializer_with_schedules(self):
        """Test that schedules are properly serialized"""
        serializer = PostSerializer(self.post)
        data = serializer.data
        
        self.assertIn('schedules', data)
        self.assertEqual(len(data['schedules']), 1)
        self.assertEqual(data['schedules'][0]['platform'], 'facebook')

    def test_post_serializer_validation(self):
        """Test PostSerializer validation"""
        valid_data = {
            'title': 'Valid Post',
            'content': 'Valid content',
            'status': 'draft',
            'media_url': 'https://example.com/image.jpg'
        }
        serializer = PostSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_post_serializer_invalid_data(self):
        """Test PostSerializer with invalid data"""
        invalid_data = {
            'title': '',  # Empty title should be invalid
            'content': 'Valid content',
            'status': 'invalid_status'  # Invalid status
        }
        serializer = PostSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('status', serializer.errors)


class ScheduleSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='This is a test post content',
            status='draft'
        )
        self.schedule = Schedule.objects.create(
            post=self.post,
            platform='facebook',
            scheduled_time=timezone.now() + timedelta(hours=1)
        )

    def test_schedule_serializer_fields(self):
        """Test that ScheduleSerializer includes all required fields"""
        serializer = ScheduleSerializer(self.schedule)
        data = serializer.data
        
        expected_fields = [
            'id', 'post', 'scheduled_time', 'platform', 'is_published',
            'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)

    def test_schedule_serializer_read_only_fields(self):
        """Test that read-only fields are properly handled"""
        serializer = ScheduleSerializer(self.schedule)
        data = serializer.data
        
        read_only_fields = ['created_at', 'updated_at']
        for field in read_only_fields:
            self.assertIn(field, data)

    def test_schedule_serializer_validation(self):
        """Test ScheduleSerializer validation"""
        valid_data = {
            'post': self.post.id,
            'platform': 'instagram',
            'scheduled_time': (timezone.now() + timedelta(hours=2)).isoformat(),
            'is_published': False
        }
        serializer = ScheduleSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())


class PostViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='This is a test post content',
            status='draft'
        )

    def test_list_posts(self):
        """Test listing posts for authenticated user"""
        url = reverse('post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Post')

    def test_create_post(self):
        """Test creating a new post"""
        url = reverse('post-list')
        data = {
            'title': 'New Post',
            'content': 'New post content',
            'status': 'draft',
            'media_url': 'https://example.com/image.jpg'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Post')
        self.assertEqual(response.data['user'], self.user.id)

    def test_retrieve_post(self):
        """Test retrieving a specific post"""
        url = reverse('post-detail', args=[self.post.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_update_post(self):
        """Test updating a post"""
        url = reverse('post-detail', args=[self.post.id])
        data = {
            'title': 'Updated Post',
            'content': 'Updated content',
            'status': 'published'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Post')
        self.assertEqual(response.data['status'], 'published')

    def test_partial_update_post(self):
        """Test partially updating a post"""
        url = reverse('post-detail', args=[self.post.id])
        data = {'title': 'Partially Updated Post'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Partially Updated Post')
        self.assertEqual(response.data['content'], 'This is a test post content')  # Unchanged

    def test_delete_post(self):
        """Test deleting a post"""
        url = reverse('post-detail', args=[self.post.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_user_can_only_see_own_posts(self):
        """Test that users can only see their own posts"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_post = Post.objects.create(
            user=other_user,
            title='Other User Post',
            content='Other user content',
            status='draft'
        )
        
        url = reverse('post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only own post
        self.assertEqual(response.data[0]['title'], 'Test Post')

    def test_schedule_post_action(self):
        """Test scheduling a post"""
        url = reverse('post-schedule', args=[self.post.id])
        scheduled_time = (timezone.now() + timedelta(hours=2)).isoformat()
        data = {
            'platform': 'facebook',
            'scheduled_time': scheduled_time
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['platform'], 'facebook')
        self.assertEqual(Schedule.objects.count(), 1)
        
        # Check that post status was updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'scheduled')

    def test_schedule_post_missing_data(self):
        """Test scheduling a post with missing required data"""
        url = reverse('post-schedule', args=[self.post.id])
        data = {'platform': 'facebook'}  # Missing scheduled_time
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_publish_post_action(self):
        """Test publishing a scheduled post"""
        # First schedule the post
        self.post.status = 'scheduled'
        self.post.save()
        
        url = reverse('post-publish', args=[self.post.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'published')
        self.assertIsNotNone(response.data['published_at'])

    def test_publish_non_scheduled_post(self):
        """Test publishing a post that is not scheduled"""
        url = reverse('post-publish', args=[self.post.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access posts"""
        self.client.force_authenticate(user=None)
        url = reverse('post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ScheduleViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='This is a test post content',
            status='draft'
        )
        self.schedule = Schedule.objects.create(
            post=self.post,
            platform='facebook',
            scheduled_time=timezone.now() + timedelta(hours=1)
        )

    def test_list_schedules(self):
        """Test listing schedules for authenticated user"""
        url = reverse('schedule-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['platform'], 'facebook')

    def test_create_schedule(self):
        """Test creating a new schedule"""
        url = reverse('schedule-list')
        scheduled_time = (timezone.now() + timedelta(hours=3)).isoformat()
        data = {
            'post': self.post.id,
            'platform': 'instagram',
            'scheduled_time': scheduled_time,
            'is_published': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 2)
        self.assertEqual(response.data['platform'], 'instagram')

    def test_retrieve_schedule(self):
        """Test retrieving a specific schedule"""
        url = reverse('schedule-detail', args=[self.schedule.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['platform'], 'facebook')

    def test_update_schedule(self):
        """Test updating a schedule"""
        url = reverse('schedule-detail', args=[self.schedule.id])
        new_scheduled_time = (timezone.now() + timedelta(hours=4)).isoformat()
        data = {
            'post': self.post.id,
            'platform': 'twitter',
            'scheduled_time': new_scheduled_time,
            'is_published': True
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['platform'], 'twitter')
        self.assertTrue(response.data['is_published'])

    def test_delete_schedule(self):
        """Test deleting a schedule"""
        url = reverse('schedule-detail', args=[self.schedule.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Schedule.objects.count(), 0)

    def test_user_can_only_see_own_schedules(self):
        """Test that users can only see schedules for their own posts"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_post = Post.objects.create(
            user=other_user,
            title='Other User Post',
            content='Other user content',
            status='draft'
        )
        other_schedule = Schedule.objects.create(
            post=other_post,
            platform='instagram',
            scheduled_time=timezone.now() + timedelta(hours=1)
        )
        
        url = reverse('schedule-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only own schedule
        self.assertEqual(response.data[0]['platform'], 'facebook')

    def test_mark_as_published_action(self):
        """Test marking a schedule as published"""
        url = reverse('schedule-mark-as-published', args=[self.schedule.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_published'])
        
        # Verify the change was saved
        self.schedule.refresh_from_db()
        self.assertTrue(self.schedule.is_published)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access schedules"""
        self.client.force_authenticate(user=None)
        url = reverse('schedule-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ContentAppIntegrationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_complete_post_workflow(self):
        """Test a complete workflow: create post, schedule it, publish it"""
        # 1. Create a post
        post_url = reverse('post-list')
        post_data = {
            'title': 'Workflow Test Post',
            'content': 'This is a test of the complete workflow',
            'status': 'draft'
        }
        post_response = self.client.post(post_url, post_data, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        post_id = post_response.data['id']

        # 2. Schedule the post
        schedule_url = reverse('post-schedule', args=[post_id])
        scheduled_time = (timezone.now() + timedelta(hours=1)).isoformat()
        schedule_data = {
            'platform': 'facebook',
            'scheduled_time': scheduled_time
        }
        schedule_response = self.client.post(schedule_url, schedule_data, format='json')
        self.assertEqual(schedule_response.status_code, status.HTTP_200_OK)

        # 3. Publish the post
        publish_url = reverse('post-publish', args=[post_id])
        publish_response = self.client.post(publish_url)
        self.assertEqual(publish_response.status_code, status.HTTP_200_OK)
        self.assertEqual(publish_response.data['status'], 'published')

        # 4. Verify the schedule was created
        schedule_list_url = reverse('schedule-list')
        schedule_list_response = self.client.get(schedule_list_url)
        self.assertEqual(schedule_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(schedule_list_response.data), 1)
        self.assertEqual(schedule_list_response.data[0]['platform'], 'facebook')

    def test_multiple_platforms_scheduling(self):
        """Test scheduling a post for multiple platforms"""
        # Create a post
        post_url = reverse('post-list')
        post_data = {
            'title': 'Multi-Platform Post',
            'content': 'This post will be scheduled for multiple platforms',
            'status': 'draft'
        }
        post_response = self.client.post(post_url, post_data, format='json')
        post_id = post_response.data['id']

        # Schedule for multiple platforms
        platforms = ['facebook', 'instagram', 'twitter']
        scheduled_time = (timezone.now() + timedelta(hours=2)).isoformat()
        
        for platform in platforms:
            schedule_url = reverse('post-schedule', args=[post_id])
            schedule_data = {
                'platform': platform,
                'scheduled_time': scheduled_time
            }
            response = self.client.post(schedule_url, schedule_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all schedules were created
        schedule_list_url = reverse('schedule-list')
        schedule_list_response = self.client.get(schedule_list_url)
        self.assertEqual(len(schedule_list_response.data), 3)
        
        created_platforms = [schedule['platform'] for schedule in schedule_list_response.data]
        for platform in platforms:
            self.assertIn(platform, created_platforms)


class CommentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='otheruser', password='testpass')
        self.post = Post.objects.create(user=self.user, content='Test post')
        self.client.login(username='testuser', password='testpass')

    def test_create_comment(self):
        url = reverse('comment-list')
        data = {'post': str(self.post.id), 'content': 'Test comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, 'Test comment')

    def test_list_comments(self):
        Comment.objects.create(post=self.post, author=self.user, content='Comment 1')
        Comment.objects.create(post=self.post, author=self.user, content='Comment 2')
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.user, content='Comment 1')
        url = reverse('comment-detail', args=[comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Comment 1')

    def test_update_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.user, content='Old content')
        url = reverse('comment-detail', args=[comment.id])
        data = {'content': 'Updated content'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Updated content')
        self.assertTrue(comment.is_edited)

    def test_delete_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.user, content='To delete')
        url = reverse('comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_reply_to_comment(self):
        parent = Comment.objects.create(post=self.post, author=self.user, content='Parent')
        url = reverse('comment-list')
        data = {'post': str(self.post.id), 'content': 'Reply', 'parent_comment': str(parent.id)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reply = Comment.objects.get(parent_comment=parent)
        self.assertEqual(reply.content, 'Reply')

    def test_like_and_unlike_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.user, content='Like me')
        url = reverse('comment-like', args=[comment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'liked')
        comment.refresh_from_db()
        self.assertEqual(comment.like_count, 1)
        # Unlike
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'unliked')
        comment.refresh_from_db()
        self.assertEqual(comment.like_count, 0)

    def test_my_comments(self):
        Comment.objects.create(post=self.post, author=self.user, content='Mine')
        Comment.objects.create(post=self.post, author=self.user2, content='Not mine')
        url = reverse('comment-my-comments')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Mine')

    def test_only_author_can_edit_or_delete(self):
        comment = Comment.objects.create(post=self.post, author=self.user2, content='Not yours')
        url = reverse('comment-detail', args=[comment.id])
        # Try to edit
        response = self.client.patch(url, {'content': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Try to delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
