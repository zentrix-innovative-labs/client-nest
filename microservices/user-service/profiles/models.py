import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class UserProfile(models.Model):
    """Extended user profile model"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    RELATIONSHIP_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('relationship', 'In a relationship'),
        ('complicated', 'It\'s complicated'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctorate', 'Doctorate'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, default='')
    phone_number = PhoneNumberField(blank=True, null=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=255, blank=True, default='')
    address_line_2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    
    # Professional Information
    occupation = models.CharField(max_length=100, blank=True, default='')
    company = models.CharField(max_length=100, blank=True, default='')
    education_level = models.CharField(
        max_length=20, 
        choices=EDUCATION_LEVEL_CHOICES, 
        blank=True,
        default=''
    )
    
    # Social Information
    relationship_status = models.CharField(
        max_length=20, 
        choices=RELATIONSHIP_STATUS_CHOICES, 
        blank=True,
        default=''
    )
    website = models.URLField(blank=True, default='')
    
    # Social Media Links
    facebook_url = models.URLField(blank=True, default='')
    twitter_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    instagram_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    
    # Interests and Preferences
    interests = models.TextField(blank=True, help_text="Comma-separated interests", default='')
    bio_extended = models.TextField(blank=True, max_length=1000, default='')
    
    # Privacy Settings
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    show_address = models.BooleanField(default=False)
    show_birth_date = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - Profile"
    
    @property
    def age(self):
        """Calculate user's age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in address_parts if part])
    
    @property
    def interests_list(self):
        """Get interests as a list"""
        if self.interests:
            return [interest.strip() for interest in self.interests.split(',') if interest.strip()]
        return []
    
    def get_social_links(self):
        """Get all social media links"""
        links = {}
        if self.facebook_url:
            links['facebook'] = self.facebook_url
        if self.twitter_url:
            links['twitter'] = self.twitter_url
        if self.linkedin_url:
            links['linkedin'] = self.linkedin_url
        if self.instagram_url:
            links['instagram'] = self.instagram_url
        if self.github_url:
            links['github'] = self.github_url
        if self.website:
            links['website'] = self.website
        return links
    
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            'date_of_birth', 'gender', 'phone_number', 'address_line_1',
            'city', 'country', 'occupation', 'bio_extended'
        ]
        
        completed_fields = 0
        total_fields = len(fields_to_check)
        
        for field in fields_to_check:
            if getattr(self, field):
                completed_fields += 1
        
        return int((completed_fields / total_fields) * 100)


class UserPreference(models.Model):
    """User preferences and settings"""
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # UI Preferences
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    # Privacy Preferences
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends', 'Friends Only'),
            ('private', 'Private'),
        ],
        default='public'
    )
    show_online_status = models.BooleanField(default=True)
    allow_friend_requests = models.BooleanField(default=True)
    
    # Content Preferences
    content_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    mature_content = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.email} - Preferences"


class UserSkill(models.Model):
    """User skills and expertise"""
    
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Novice'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.IntegerField(
        choices=PROFICIENCY_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_skills'
        verbose_name = 'User Skill'
        verbose_name_plural = 'User Skills'
        unique_together = ['user', 'skill_name']
        ordering = ['-proficiency_level', 'skill_name']
    
    def __str__(self):
        return f"{self.user.email} - {self.skill_name} ({self.get_proficiency_level_display()})"


class UserEducation(models.Model):
    """User education history"""
    
    DEGREE_CHOICES = [
        ('high_school', 'High School Diploma'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctorate', 'Doctorate'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education')
    
    institution_name = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )
    description = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_education'
        verbose_name = 'User Education'
        verbose_name_plural = 'User Education'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.institution_name} ({self.get_degree_type_display()})"


class UserExperience(models.Model):
    """User work experience"""
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('volunteer', 'Volunteer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experience')
    
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    location = models.CharField(max_length=100, blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_experience'
        verbose_name = 'User Experience'
        verbose_name_plural = 'User Experience'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.job_title} at {self.company_name}"
    
    @property
    def duration(self):
        """Calculate duration of employment"""
        end = self.end_date or timezone.now().date()
        duration = end - self.start_date
        
        years = duration.days // 365
        months = (duration.days % 365) // 30
        
        if years > 0:
            return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"
        else:
            return f"{months} month{'s' if months != 1 else ''}"