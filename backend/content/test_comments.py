from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Post, Comment, CommentLike

User = get_user_model()

class CommentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com',
            password='testpass'
        )
        self.user2 = User.objects.create_user(
            username='otheruser', 
            email='otheruser@example.com',
            password='testpass'
        )
        self.post = Post.objects.create(user=self.user, content='Test post')
        self.client.force_authenticate(user=self.user)

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

    def test_filter_comments_by_post(self):
        post2 = Post.objects.create(user=self.user, content='Another post')
        c1 = Comment.objects.create(post=self.post, author=self.user, content='Comment on post1')
        c2 = Comment.objects.create(post=post2, author=self.user, content='Comment on post2')
        url = reverse('comment-list')
        response = self.client.get(url, {'post': str(self.post.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Comment on post1')

    def test_filter_comments_by_author(self):
        c1 = Comment.objects.create(post=self.post, author=self.user, content='Mine')
        c2 = Comment.objects.create(post=self.post, author=self.user2, content='Not mine')
        url = reverse('comment-list')
        response = self.client.get(url, {'author': str(self.user.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Mine')

    def test_filter_comments_by_parent_comment(self):
        parent = Comment.objects.create(post=self.post, author=self.user, content='Parent')
        reply = Comment.objects.create(post=self.post, author=self.user, content='Reply', parent_comment=parent)
        url = reverse('comment-list')
        response = self.client.get(url, {'parent_comment': str(parent.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Reply')

    def test_search_comments_by_content(self):
        Comment.objects.create(post=self.post, author=self.user, content='FindMe')
        Comment.objects.create(post=self.post, author=self.user, content='Other comment')
        url = reverse('comment-list')
        response = self.client.get(url, {'search': 'FindMe'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'FindMe')

    def test_order_comments_by_like_count(self):
        c1 = Comment.objects.create(post=self.post, author=self.user, content='First')
        c2 = Comment.objects.create(post=self.post, author=self.user, content='Second')
        # Like c2 twice
        CommentLike.objects.create(comment=c2, user=self.user)
        CommentLike.objects.create(comment=c2, user=self.user2)
        url = reverse('comment-list')
        response = self.client.get(url, {'ordering': '-like_count'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['content'], 'Second')

    def test_order_comments_by_created_at(self):
        c1 = Comment.objects.create(post=self.post, author=self.user, content='Oldest')
        c2 = Comment.objects.create(post=self.post, author=self.user, content='Newest')
        url = reverse('comment-list')
        response = self.client.get(url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['content'], 'Newest')

    def test_list_comment_likes(self):
        comment = Comment.objects.create(post=self.post, author=self.user, content='Likeable')
        CommentLike.objects.create(comment=comment, user=self.user)
        url = reverse('comment-like-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['comment'], comment.id)
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_create_comment_like(self):
        comment = Comment.objects.create(post=self.post, author=self.user2, content='Like me')
        url = reverse('commentlike-list')
        data = {'comment': comment.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommentLike.objects.count(), 1)
        self.assertEqual(CommentLike.objects.first().comment, comment)
        self.assertEqual(CommentLike.objects.first().user, self.user)

    def test_delete_comment_like(self):
        comment = Comment.objects.create(post=self.post, author=self.user2, content='Like me')
        like = CommentLike.objects.create(comment=comment, user=self.user)
        url = reverse('commentlike-detail', args=[like.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CommentLike.objects.count(), 0) 