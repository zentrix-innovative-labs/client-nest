"""
Test file to verify password validation in serializers
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from .serializers import (
    UserRegistrationSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()


class PasswordValidationTestCase(TestCase):
    """Test password validation in serializers"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
    
    def test_user_registration_password_validation(self):
        """Test password validation in user registration"""
        # Test mismatched passwords
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password_confirm': 'differentpassword123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)
        
        # Test matching passwords
        data['password_confirm'] = 'newpassword123'
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_registration_weak_password(self):
        """Test weak password validation"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',  # Too weak
            'password_confirm': '123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_change_password_validation(self):
        """Test password change validation"""
        request = self.factory.post('/')
        request.user = self.user
        
        # Test incorrect old password
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
        
        # Test same new password as old
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'oldpassword123',
            'new_password_confirm': 'oldpassword123'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)
        
        # Test mismatched new passwords
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'differentpassword123'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)
        
        # Test valid password change
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
    
    def test_password_reset_confirm_validation(self):
        """Test password reset confirmation validation"""
        # Test mismatched passwords
        data = {
            'new_password': 'newpassword123',
            'new_password_confirm': 'differentpassword123'
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)
        
        # Test matching passwords
        data['new_password_confirm'] = 'newpassword123'
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        data = {
            'username': 'hasheduser',
            'email': 'hashed@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        
        # Password should be hashed, not stored in plain text
        self.assertNotEqual(user.password, 'testpassword123')
        self.assertTrue(user.check_password('testpassword123'))
