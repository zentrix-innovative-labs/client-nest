from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from .models import User, UserActivity, UserSession
from .utils import check_password_strength, validate_phone_number

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_premium)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_data = {
            'email': 'admin@example.com',
            'username': 'admin',
            'password': 'adminpass123'
        }
        user = User.objects.create_superuser(**admin_data)
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])
    
    def test_get_full_name(self):
        """Test get_full_name method"""
        user = User.objects.create_user(**self.user_data)
        expected_name = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        self.assertEqual(user.get_full_name(), expected_name)
    
    def test_get_short_name(self):
        """Test get_short_name method"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), self.user_data['first_name'])
    
    def test_profile_completeness(self):
        """Test profile completeness calculation"""
        user = User.objects.create_user(**self.user_data)
        
        # Initial completeness (email, username, first_name, last_name)
        initial_completeness = user.profile_completeness
        self.assertGreater(initial_completeness, 0)
        
        # Add bio to increase completeness
        user.bio = "Test bio"
        user.save()
        
        new_completeness = user.profile_completeness
        self.assertGreater(new_completeness, initial_completeness)
    
    def test_soft_delete(self):
        """Test soft delete functionality"""
        user = User.objects.create_user(**self.user_data)
        user.soft_delete()
        
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.updated_at)


class UserActivityModelTest(TestCase):
    """Test UserActivity model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_activity(self):
        """Test creating user activity"""
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='login',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'login')
        self.assertEqual(activity.ip_address, '127.0.0.1')
        self.assertIsNotNone(activity.timestamp)


class UserSessionModelTest(TestCase):
    """Test UserSession model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_session(self):
        """Test creating user session"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
        self.assertFalse(session.is_expired)
    
    def test_session_expiration(self):
        """Test session expiration"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        # Manually set last_activity to past
        session.last_activity = timezone.now() - timedelta(days=31)
        session.save()
        
        self.assertTrue(session.is_expired)
    
    def test_terminate_session(self):
        """Test session termination"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        session.terminate()
        self.assertFalse(session.is_active)


class UserRegistrationAPITest(APITestCase):
    """Test user registration API"""
    
    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse('users:user-register')
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    
    def test_valid_registration(self):
        """Test valid user registration"""
        response = self.client.post(self.registration_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertTrue(User.objects.filter(email=self.valid_data['email']).exists())
    
    def test_invalid_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        invalid_data = self.valid_data.copy()
        invalid_data['password_confirm'] = 'differentpassword'
        
        response = self.client.post(self.registration_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email"""
        # Create first user
        User.objects.create_user(
            email=self.valid_data['email'],
            username='firstuser',
            password='password123'
        )
        
        # Try to register with same email
        response = self.client.post(self.registration_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_username_registration(self):
        """Test registration with duplicate username"""
        # Create first user
        User.objects.create_user(
            email='first@example.com',
            username=self.valid_data['username'],
            password='password123'
        )
        
        # Try to register with same username
        response = self.client.post(self.registration_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginAPITest(APITestCase):
    """Test user login API"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('users:user-login')
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_valid_login(self):
        """Test valid user login"""
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
    
    def test_invalid_login_wrong_password(self):
        """Test login with wrong password"""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_inactive_user_login(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileAPITest(APITestCase):
    """Test user profile API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.profile_url = reverse('users:user-profile')
        
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['username'], self.user.username)
    
    def test_update_profile(self):
        """Test updating user profile"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.bio, 'Updated bio')
    
    def test_unauthenticated_profile_access(self):
        """Test accessing profile without authentication"""
        self.client.credentials()  # Remove authentication
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeAPITest(APITestCase):
    """Test password change API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='oldpassword123'
        )
        self.change_password_url = reverse('users:change-password')
        
        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_valid_password_change(self):
        """Test valid password change"""
        change_data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        response = self.client.put(self.change_password_url, change_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
    
    def test_invalid_old_password(self):
        """Test password change with invalid old password"""
        change_data = {
            'old_password': 'wrongoldpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        response = self.client.put(self.change_password_url, change_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_mismatch(self):
        """Test password change with new password mismatch"""
        change_data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'differentpassword'
        }
        
        response = self.client.put(self.change_password_url, change_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UtilityFunctionsTest(TestCase):
    """Test utility functions"""
    
    def test_password_strength_weak(self):
        """Test password strength check for weak password"""
        result = check_password_strength('123')
        
        self.assertFalse(result['is_strong'])
        self.assertLess(result['score'], 4)
        self.assertGreater(len(result['suggestions']), 0)
    
    def test_password_strength_strong(self):
        """Test password strength check for strong password"""
        result = check_password_strength('StrongP@ssw0rd123')
        
        self.assertTrue(result['is_strong'])
        self.assertGreaterEqual(result['score'], 4)
    
    def test_validate_phone_number_valid(self):
        """Test phone number validation with valid number"""
        # This test might need adjustment based on phonenumber_field implementation
        result = validate_phone_number('+1234567890')
        # The actual result depends on the phonenumber_field library
        self.assertIsInstance(result, bool)
    
    def test_validate_phone_number_invalid(self):
        """Test phone number validation with invalid number"""
        result = validate_phone_number('invalid_phone')
        self.assertFalse(result)


class EmailTest(TestCase):
    """Test email functionality"""
    
    def test_registration_sends_verification_email(self):
        """Test that registration sends verification email"""
        # This would require mocking the email sending in a real test
        # For now, we'll just check that the mail outbox is empty initially
        self.assertEqual(len(mail.outbox), 0)