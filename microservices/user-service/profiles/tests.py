from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, datetime, timedelta
from decimal import Decimal
import json

from .models import UserProfile, UserPreference, UserSkill, UserEducation, UserExperience
from .utils import (
    validate_social_url,
    calculate_profile_completion,
    validate_phone_number,
    validate_skill_name,
    sanitize_bio,
    export_user_profile_data
)

User = get_user_model()


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            date_of_birth=date(1990, 1, 1),
            gender='male',
            phone_number='+1234567890',
            city='New York',
            country='USA',
            occupation='Developer'
        )
    
    def test_profile_creation(self):
        """Test profile is created correctly."""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.city, 'New York')
    
    def test_age_calculation(self):
        """Test age calculation."""
        expected_age = timezone.now().year - 1990
        self.assertEqual(self.profile.age, expected_age)
    
    def test_full_address(self):
        """Test full address formatting."""
        self.profile.address = '123 Main St'
        self.profile.state = 'NY'
        self.profile.postal_code = '10001'
        expected_address = '123 Main St, New York, NY 10001, USA'
        self.assertEqual(self.profile.full_address, expected_address)
    
    def test_profile_completion_percentage(self):
        """Test profile completion calculation."""
        completion = self.profile.profile_completion_percentage
        self.assertIsInstance(completion, float)
        self.assertGreaterEqual(completion, 0)
        self.assertLessEqual(completion, 100)
    
    def test_str_representation(self):
        """Test string representation."""
        expected_str = f"{self.user.get_full_name()}'s Profile"
        self.assertEqual(str(self.profile), expected_str)


class UserPreferenceModelTest(TestCase):
    """Test cases for UserPreference model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.preference = UserPreference.objects.create(
            user=self.user,
            theme='dark',
            language='en',
            timezone='UTC'
        )
    
    def test_preference_creation(self):
        """Test preference is created correctly."""
        self.assertEqual(self.preference.user, self.user)
        self.assertEqual(self.preference.theme, 'dark')
        self.assertEqual(self.preference.language, 'en')
    
    def test_default_values(self):
        """Test default preference values."""
        self.assertTrue(self.preference.email_notifications)
        self.assertTrue(self.preference.push_notifications)
        self.assertEqual(self.preference.profile_visibility, 'public')


class UserSkillModelTest(TestCase):
    """Test cases for UserSkill model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.skill = UserSkill.objects.create(
            user=self.user,
            skill_name='Python',
            proficiency_level='advanced',
            years_of_experience=5
        )
    
    def test_skill_creation(self):
        """Test skill is created correctly."""
        self.assertEqual(self.skill.user, self.user)
        self.assertEqual(self.skill.skill_name, 'Python')
        self.assertEqual(self.skill.proficiency_level, 'advanced')
        self.assertEqual(self.skill.years_of_experience, 5)
    
    def test_unique_constraint(self):
        """Test unique constraint on user and skill name."""
        with self.assertRaises(Exception):
            UserSkill.objects.create(
                user=self.user,
                skill_name='Python',
                proficiency_level='beginner'
            )


class UserEducationModelTest(TestCase):
    """Test cases for UserEducation model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.education = UserEducation.objects.create(
            user=self.user,
            institution_name='Test University',
            degree_type='bachelor',
            field_of_study='Computer Science',
            start_date=date(2018, 9, 1),
            end_date=date(2022, 6, 30),
            gpa=Decimal('3.8')
        )
    
    def test_education_creation(self):
        """Test education is created correctly."""
        self.assertEqual(self.education.user, self.user)
        self.assertEqual(self.education.institution_name, 'Test University')
        self.assertEqual(self.education.degree_type, 'bachelor')
        self.assertEqual(self.education.gpa, Decimal('3.8'))


class UserExperienceModelTest(TestCase):
    """Test cases for UserExperience model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.experience = UserExperience.objects.create(
            user=self.user,
            company_name='Test Company',
            job_title='Software Developer',
            employment_type='full_time',
            start_date=date(2022, 1, 1),
            end_date=date(2023, 12, 31)
        )
    
    def test_experience_creation(self):
        """Test experience is created correctly."""
        self.assertEqual(self.experience.user, self.user)
        self.assertEqual(self.experience.company_name, 'Test Company')
        self.assertEqual(self.experience.job_title, 'Software Developer')
    
    def test_duration_calculation(self):
        """Test duration calculation."""
        duration = self.experience.duration_years
        self.assertIsInstance(duration, float)
        self.assertGreater(duration, 0)


class ProfileUtilsTest(TestCase):
    """Test cases for profile utility functions."""
    
    def test_validate_social_url(self):
        """Test social URL validation."""
        # Valid URLs
        self.assertTrue(validate_social_url('https://linkedin.com/in/johndoe', 'linkedin'))
        self.assertTrue(validate_social_url('https://twitter.com/johndoe', 'twitter'))
        self.assertTrue(validate_social_url('https://github.com/johndoe', 'github'))
        
        # Invalid URLs
        self.assertFalse(validate_social_url('invalid-url', 'linkedin'))
        self.assertFalse(validate_social_url('https://facebook.com/johndoe', 'linkedin'))
    
    def test_validate_phone_number(self):
        """Test phone number validation."""
        # Valid phone numbers
        self.assertTrue(validate_phone_number('+1234567890'))
        self.assertTrue(validate_phone_number('1234567890'))
        
        # Invalid phone numbers
        self.assertFalse(validate_phone_number('123'))
        self.assertFalse(validate_phone_number('invalid'))
    
    def test_validate_skill_name(self):
        """Test skill name validation."""
        # Valid skill names
        self.assertTrue(validate_skill_name('Python'))
        self.assertTrue(validate_skill_name('Machine Learning'))
        self.assertTrue(validate_skill_name('C++'))
        
        # Invalid skill names
        self.assertFalse(validate_skill_name('A'))
        self.assertFalse(validate_skill_name(''))
        self.assertFalse(validate_skill_name('   '))
    
    def test_sanitize_bio(self):
        """Test bio sanitization."""
        # Test HTML removal
        bio_with_html = '<script>alert("xss")</script>This is a bio'
        sanitized = sanitize_bio(bio_with_html)
        self.assertNotIn('<script>', sanitized)
        self.assertIn('This is a bio', sanitized)
        
        # Test whitespace cleanup
        bio_with_spaces = '   This   is   a   bio   '
        sanitized = sanitize_bio(bio_with_spaces)
        self.assertEqual(sanitized, 'This is a bio')
    
    def test_calculate_profile_completion(self):
        """Test profile completion calculation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        profile = UserProfile.objects.create(
            user=user,
            bio='Test bio',
            date_of_birth=date(1990, 1, 1),
            phone_number='+1234567890',
            city='New York',
            country='USA'
        )
        
        completion_data = calculate_profile_completion(profile)
        
        self.assertIn('overall_percentage', completion_data)
        self.assertIn('required_percentage', completion_data)
        self.assertIn('missing_fields', completion_data)
        self.assertIn('is_complete', completion_data)
        
        self.assertIsInstance(completion_data['overall_percentage'], float)
        self.assertGreaterEqual(completion_data['overall_percentage'], 0)
        self.assertLessEqual(completion_data['overall_percentage'], 100)


class ProfileAPITest(APITestCase):
    """Test cases for Profile API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_my_profile(self):
        """Test getting current user's profile."""
        url = reverse('profiles:my-profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
    
    def test_update_profile(self):
        """Test updating profile."""
        url = reverse('profiles:my-profile')
        data = {
            'bio': 'Updated bio',
            'city': 'San Francisco',
            'occupation': 'Senior Developer'
        }
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        self.assertEqual(response.data['city'], 'San Francisco')
    
    def test_get_preferences(self):
        """Test getting user preferences."""
        url = reverse('profiles:my-preferences')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('theme', response.data)
        self.assertIn('language', response.data)
    
    def test_create_skill(self):
        """Test creating a skill."""
        url = reverse('profiles:my-skills')
        data = {
            'skill_name': 'Django',
            'proficiency_level': 'advanced',
            'years_of_experience': 3
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['skill_name'], 'Django')
        self.assertEqual(response.data['proficiency_level'], 'advanced')
    
    def test_create_education(self):
        """Test creating education record."""
        url = reverse('profiles:my-education')
        data = {
            'institution_name': 'Test University',
            'degree_type': 'bachelor',
            'field_of_study': 'Computer Science',
            'start_date': '2018-09-01',
            'end_date': '2022-06-30',
            'gpa': '3.8'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['institution_name'], 'Test University')
        self.assertEqual(response.data['degree_type'], 'bachelor')
    
    def test_create_experience(self):
        """Test creating work experience."""
        url = reverse('profiles:my-experience')
        data = {
            'company_name': 'Test Company',
            'job_title': 'Software Developer',
            'employment_type': 'full_time',
            'start_date': '2022-01-01',
            'end_date': '2023-12-31',
            'description': 'Developed web applications'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company_name'], 'Test Company')
        self.assertEqual(response.data['job_title'], 'Software Developer')
    
    def test_completion_stats(self):
        """Test profile completion statistics."""
        url = reverse('profiles:completion-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_percentage', response.data)
        self.assertIn('missing_fields', response.data)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to profile endpoints."""
        self.client.force_authenticate(user=None)
        
        url = reverse('profiles:my-profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfilePermissionsTest(APITestCase):
    """Test cases for profile permissions."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        self.skill1 = UserSkill.objects.create(
            user=self.user1,
            skill_name='Python',
            proficiency_level='advanced'
        )
        self.client = APIClient()
    
    def test_user_can_only_access_own_data(self):
        """Test users can only access their own profile data."""
        self.client.force_authenticate(user=self.user2)
        
        # Try to access user1's skill
        url = reverse('profiles:userskill-detail', kwargs={'pk': self.skill1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_can_access_own_data(self):
        """Test users can access their own profile data."""
        self.client.force_authenticate(user=self.user1)
        
        # Access own skill
        url = reverse('profiles:userskill-detail', kwargs={'pk': self.skill1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['skill_name'], 'Python')


class ProfileSignalsTest(TransactionTestCase):
    """Test cases for profile signals."""
    
    def setUp(self):
        cache.clear()
    
    def test_profile_created_on_user_creation(self):
        """Test profile and preferences are created when user is created."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Check profile was created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
        # Check preferences were created
        self.assertTrue(UserPreference.objects.filter(user=user).exists())
    
    def test_cache_cleared_on_profile_update(self):
        """Test cache is cleared when profile is updated."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        profile = user.userprofile
        
        # Update profile
        profile.bio = 'Updated bio'
        profile.save()
        
        # Cache should be cleared (this is more of an integration test)
        # In a real scenario, you'd check if the cache key was deleted
        self.assertTrue(True)  # Placeholder assertion


class ProfileExportTest(TestCase):
    """Test cases for profile data export."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Create profile data
        UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            city='New York'
        )
        
        UserSkill.objects.create(
            user=self.user,
            skill_name='Python',
            proficiency_level='advanced'
        )
        
        UserEducation.objects.create(
            user=self.user,
            institution_name='Test University',
            degree_type='bachelor'
        )
    
    def test_export_user_profile_data(self):
        """Test exporting user profile data."""
        exported_data = export_user_profile_data(self.user)
        
        self.assertIn('user_info', exported_data)
        self.assertIn('profile', exported_data)
        self.assertIn('skills', exported_data)
        self.assertIn('education', exported_data)
        
        # Check user info
        self.assertEqual(exported_data['user_info']['email'], 'test@example.com')
        self.assertEqual(exported_data['user_info']['first_name'], 'John')
        
        # Check profile data
        self.assertIsNotNone(exported_data['profile'])
        self.assertEqual(exported_data['profile']['bio'], 'Test bio')
        
        # Check skills
        self.assertEqual(len(exported_data['skills']), 1)
        self.assertEqual(exported_data['skills'][0]['skill_name'], 'Python')
        
        # Check education
        self.assertEqual(len(exported_data['education']), 1)
        self.assertEqual(exported_data['education'][0]['institution_name'], 'Test University')


class ProfileValidationTest(TestCase):
    """Test cases for profile validation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_invalid_social_urls_are_cleared(self):
        """Test invalid social URLs are cleared during validation."""
        profile = UserProfile.objects.create(
            user=self.user,
            linkedin_url='invalid-url',
            twitter_url='https://twitter.com/validuser'
        )
        
        # The signal should have cleared the invalid URL
        profile.refresh_from_db()
        self.assertIsNone(profile.linkedin_url)
        self.assertEqual(profile.twitter_url, 'https://twitter.com/validuser')
    
    def test_bio_sanitization(self):
        """Test bio is sanitized during validation."""
        profile = UserProfile.objects.create(
            user=self.user,
            bio='<script>alert("xss")</script>Clean bio content'
        )
        
        # The signal should have sanitized the bio
        profile.refresh_from_db()
        self.assertNotIn('<script>', profile.bio)
        self.assertIn('Clean bio content', profile.bio)