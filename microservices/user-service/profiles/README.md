# Profiles App

The Profiles app extends the basic user functionality by providing comprehensive user profile management, preferences, skills tracking, education history, and work experience management.

## Features

### User Profile Management
- Extended user profiles with personal information
- Address and contact details
- Professional information (occupation, company, education level)
- Social media links (LinkedIn, Twitter, Facebook, Instagram, GitHub)
- Profile and cover photos
- Privacy settings for profile visibility
- Profile completion tracking

### User Preferences
- UI preferences (theme, language, timezone)
- Notification settings (email, push, SMS, marketing)
- Privacy controls (profile visibility, online status, friend requests)
- Content preferences (language, mature content)

### Skills Management
- Skill tracking with proficiency levels
- Years of experience tracking
- Skill verification system
- Skill validation and normalization

### Education History
- Multiple education records
- Institution and degree information
- GPA tracking
- Date validation

### Work Experience
- Employment history tracking
- Company and position details
- Employment type classification
- Duration calculation
- Current position tracking

## Models

### UserProfile
Extended user profile information including:
- Personal details (date of birth, gender, phone)
- Address information
- Professional details
- Social media links
- Privacy settings
- Profile completion calculation

### UserPreference
User preferences and settings for:
- UI customization
- Notification preferences
- Privacy controls
- Content settings

### UserSkill
Skill tracking with:
- Skill name and proficiency level
- Years of experience
- Verification status
- Unique constraint per user

### UserEducation
Education history including:
- Institution and degree information
- Field of study
- Date ranges
- GPA tracking

### UserExperience
Work experience tracking:
- Company and position details
- Employment type
- Date ranges
- Current position flag

## API Endpoints

### Profile Management
- `GET /api/v1/profiles/` - List profiles
- `POST /api/v1/profiles/` - Create profile
- `GET /api/v1/profiles/{id}/` - Get specific profile
- `PUT /api/v1/profiles/{id}/` - Update profile
- `DELETE /api/v1/profiles/{id}/` - Delete profile
- `GET /api/v1/profiles/my_profile/` - Get current user's profile
- `POST /api/v1/profiles/create_profile/` - Create profile for current user
- `GET /api/v1/profiles/{id}/completion_stats/` - Get completion statistics

### Preferences
- `GET /api/v1/profiles/preferences/` - List preferences
- `POST /api/v1/profiles/preferences/` - Create preferences
- `GET /api/v1/profiles/preferences/{id}/` - Get specific preferences
- `PUT /api/v1/profiles/preferences/{id}/` - Update preferences
- `GET /api/v1/profiles/preferences/my_preferences/` - Get current user's preferences

### Skills
- `GET /api/v1/profiles/skills/` - List skills
- `POST /api/v1/profiles/skills/` - Add skill
- `GET /api/v1/profiles/skills/{id}/` - Get specific skill
- `PUT /api/v1/profiles/skills/{id}/` - Update skill
- `DELETE /api/v1/profiles/skills/{id}/` - Delete skill
- `GET /api/v1/profiles/skills/my_skills/` - Get current user's skills
- `GET /api/v1/profiles/skills/skill_summary/` - Get skill summary

### Education
- `GET /api/v1/profiles/education/` - List education
- `POST /api/v1/profiles/education/` - Add education
- `GET /api/v1/profiles/education/{id}/` - Get specific education
- `PUT /api/v1/profiles/education/{id}/` - Update education
- `DELETE /api/v1/profiles/education/{id}/` - Delete education
- `GET /api/v1/profiles/education/my_education/` - Get current user's education

### Experience
- `GET /api/v1/profiles/experience/` - List experience
- `POST /api/v1/profiles/experience/` - Add experience
- `GET /api/v1/profiles/experience/{id}/` - Get specific experience
- `PUT /api/v1/profiles/experience/{id}/` - Update experience
- `DELETE /api/v1/profiles/experience/{id}/` - Delete experience
- `GET /api/v1/profiles/experience/my_experience/` - Get current user's experience
- `GET /api/v1/profiles/experience/career_summary/` - Get career summary

### Complete Profile
- `GET /api/v1/profiles/complete-profile/` - Get complete profile data
- `GET /api/v1/profiles/complete-profile/complete-profile-me/` - Get current user's complete profile
- `POST /api/v1/profiles/complete-profile/complete-profile-bulk-create/` - Bulk create profile data

### Utility Endpoints
- `GET /api/v1/profiles/export-data/` - Export user data (GDPR)
- `POST /api/v1/profiles/validate-social-url/` - Validate social media URLs
- `POST /api/v1/profiles/validate-phone/` - Validate phone numbers
- `POST /api/v1/profiles/validate-skill/` - Validate skill names
- `GET /api/v1/profiles/analytics/` - Get profile analytics
- `POST /api/v1/profiles/username-suggestions/` - Generate username suggestions

## Permissions

The app uses custom permission classes:
- `IsOwnerOrReadOnly` - Users can only modify their own data
- `IsProfileOwner` - Profile-specific ownership
- `CanViewProfile` - Privacy-aware profile viewing
- `CanModifyProfile` - Profile modification permissions
- `IsVerifiedUser` - Verified user requirements
- `IsPremiumUser` - Premium feature access
- `RateLimitPermission` - Rate limiting for updates

## Signals

Automatic profile management through Django signals:
- Auto-create profile and preferences on user creation
- Cache management on profile updates
- Profile completion tracking
- Activity logging
- Data validation on save

## Utilities

Helper functions for:
- Social media URL validation
- Phone number validation
- Profile completion calculation
- Username generation
- Data export (GDPR compliance)
- Profile analytics
- Caching management

## Testing

Comprehensive test suite covering:
- Model functionality
- API endpoints
- Permissions
- Signals
- Utility functions
- Data validation
- Export functionality

## Usage Examples

### Creating a Profile
```python
POST /api/v1/profiles/create_profile/
{
    "date_of_birth": "1990-01-01",
    "gender": "M",
    "phone_number": "+1234567890",
    "city": "New York",
    "country": "USA",
    "occupation": "Software Engineer",
    "bio_extended": "Passionate developer..."
}
```

### Adding Skills
```python
POST /api/v1/profiles/skills/
{
    "skill_name": "Python",
    "proficiency_level": "advanced",
    "years_of_experience": 5
}
```

### Bulk Profile Creation
```python
POST /api/v1/profiles/complete-profile/complete-profile-bulk-create/
{
    "profile": {...},
    "preferences": {...},
    "skills": [...],
    "education": [...],
    "experience": [...]
}
```

## Security Features

- Input validation and sanitization
- XSS prevention in bio content
- Privacy controls for profile visibility
- Rate limiting on profile updates
- GDPR-compliant data export
- Secure file upload handling
- Permission-based access control

## Performance Optimizations

- Redis caching for profile data
- Database query optimization
- Selective field loading
- Efficient serialization
- Background task processing
- Image optimization

## Integration

The profiles app integrates with:
- User authentication system
- Activity logging
- Email notifications
- File storage (for images)
- Cache management
- Background task processing