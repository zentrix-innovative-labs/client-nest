# ClientNest User Service API Endpoints

## Base URL: `http://127.0.0.1:8000`

---

## 🏠 Service Information

### Root Service Info
- **GET** `/` - Service information and available endpoints

### Health & Monitoring
- **GET** `/health/` - Health check endpoint
- **GET** `/health-check/` - Detailed health checks

---

## 📚 API Documentation

### Interactive Documentation
- **GET** `/swagger/` - Swagger UI (Interactive API docs)
- **GET** `/redoc/` - ReDoc documentation
- **GET** `/swagger.json` - OpenAPI JSON schema

---

## 🔐 Authentication & Authorization

### User Registration & Login
- **POST** `http://127.0.0.1:8000/api/v1/users/auth/register/` - Register new user
- **POST** `http://127.0.0.1:8000/api/v1/users/auth/login/` - User login
- **POST** `http://127.0.0.1:8000/api/v1/users/auth/logout/` - User logout
- **POST** `http://127.0.0.1:8000/api/v1/users/auth/refresh/` - Refresh JWT token

### Password Management
- **POST** `http://127.0.0.1:8000/api/v1/users/auth/change-password/` - Change password (authenticated)
- **POST** `http://127.0.0.1:8000/api/v1/users/auth/reset-password/` - Request password reset
- **POST** `http://127.0.0.1:8000/api/v1/users/auth/reset-password/<uidb64>/<token>/` - Confirm password reset

### Email Verification
- **GET** `/api/v1/users/auth/verify-email/<uidb64>/<token>/` - Verify email
- **POST** `/api/v1/users/auth/resend-verification/` - Resend verification email

---

## 👤 User Management

### User CRUD Operations
- **GET** `/api/v1/users/users/` - List users (paginated)
- **POST** `/api/v1/users/users/` - Create new user
- **GET** `/api/v1/users/users/{id}/` - Get user details
- **PUT** `/api/v1/users/users/{id}/` - Update user (full)
- **PATCH** `/api/v1/users/users/{id}/` - Update user (partial)
- **DELETE** `/api/v1/users/users/{id}/` - Delete user

### User Profile
- **GET** `/api/v1/users/profile/` - Get current user profile
- **PUT** `/api/v1/users/profile/` - Update current user profile
- **PATCH** `/api/v1/users/profile/` - Partially update profile

### User Activities
- **GET** `/api/v1/users/activities/` - List user activities
- **GET** `/api/v1/users/activities/{id}/` - Get specific activity

### User Sessions
- **GET** `/api/v1/users/sessions/` - List active sessions
- **GET** `/api/v1/users/sessions/{id}/` - Get session details
- **DELETE** `/api/v1/users/sessions/{id}/` - Terminate session

---

## 👨‍💼 User Profiles

### Profile Management
- **GET** `/api/v1/profiles/my-profile/` - Get my profile
- **POST** `/api/v1/profiles/my-profile/` - Create profile
- **PUT** `/api/v1/profiles/my-profile/` - Update profile
- **PATCH** `/api/v1/profiles/my-profile/` - Partial update profile

### Profile Data
- **GET** `/api/v1/profiles/profiles/` - List all profiles
- **GET** `/api/v1/profiles/profiles/{id}/` - Get specific profile
- **POST** `/api/v1/profiles/profiles/` - Create profile
- **PUT** `/api/v1/profiles/profiles/{id}/` - Update profile
- **PATCH** `/api/v1/profiles/profiles/{id}/` - Partial update profile
- **DELETE** `/api/v1/profiles/profiles/{id}/` - Delete profile

---

## ⚙️ User Preferences

### Preferences Management
- **GET** `/api/v1/profiles/my-preferences/` - Get my preferences
- **PUT** `/api/v1/profiles/my-preferences/` - Update preferences
- **PATCH** `/api/v1/profiles/my-preferences/` - Partial update preferences

### Preferences CRUD
- **GET** `/api/v1/profiles/preferences/` - List preferences
- **POST** `/api/v1/profiles/preferences/` - Create preferences
- **GET** `/api/v1/profiles/preferences/{id}/` - Get preferences
- **PUT** `/api/v1/profiles/preferences/{id}/` - Update preferences
- **PATCH** `/api/v1/profiles/preferences/{id}/` - Partial update preferences
- **DELETE** `/api/v1/profiles/preferences/{id}/` - Delete preferences

---

## 🎯 Skills Management

### My Skills
- **GET** `/api/v1/profiles/my-skills/` - Get my skills
- **POST** `/api/v1/profiles/my-skills/` - Add skill

### Skills CRUD
- **GET** `/api/v1/profiles/skills/` - List all skills
- **POST** `/api/v1/profiles/skills/` - Create skill
- **GET** `/api/v1/profiles/skills/{id}/` - Get skill details
- **PUT** `/api/v1/profiles/skills/{id}/` - Update skill
- **PATCH** `/api/v1/profiles/skills/{id}/` - Partial update skill
- **DELETE** `/api/v1/profiles/skills/{id}/` - Delete skill

### Skills Analytics
- **GET** `/api/v1/profiles/skill-summary/` - Get skills summary

---

## 🎓 Education Management

### My Education
- **GET** `/api/v1/profiles/my-education/` - Get my education
- **POST** `/api/v1/profiles/my-education/` - Add education

### Education CRUD
- **GET** `/api/v1/profiles/education/` - List education records
- **POST** `/api/v1/profiles/education/` - Create education record
- **GET** `/api/v1/profiles/education/{id}/` - Get education details
- **PUT** `/api/v1/profiles/education/{id}/` - Update education
- **PATCH** `/api/v1/profiles/education/{id}/` - Partial update education
- **DELETE** `/api/v1/profiles/education/{id}/` - Delete education

---

## 💼 Work Experience

### My Experience
- **GET** `/api/v1/profiles/my-experience/` - Get my experience
- **POST** `/api/v1/profiles/my-experience/` - Add experience

### Experience CRUD
- **GET** `/api/v1/profiles/experience/` - List experience records
- **POST** `/api/v1/profiles/experience/` - Create experience record
- **GET** `/api/v1/profiles/experience/{id}/` - Get experience details
- **PUT** `/api/v1/profiles/experience/{id}/` - Update experience
- **PATCH** `/api/v1/profiles/experience/{id}/` - Partial update experience
- **DELETE** `/api/v1/profiles/experience/{id}/` - Delete experience

### Career Analytics
- **GET** `/api/v1/profiles/career-summary/` - Get career summary

---

## 📊 Profile Analytics & Stats

### Completion & Analytics
- **GET** `/api/v1/profiles/completion-stats/` - Profile completion statistics
- **GET** `/api/v1/profiles/analytics/` - Profile analytics data

### Complete Profile
- **GET** `/api/v1/profiles/complete-profile/me/` - Get complete profile
- **POST** `/api/v1/profiles/complete-profile/bulk-create/` - Bulk create profile data

---

## ✅ Validation Endpoints

### Data Validation
- **POST** `/api/v1/profiles/validate-social-url/` - Validate social media URL
- **POST** `/api/v1/profiles/validate-phone/` - Validate phone number
- **POST** `/api/v1/profiles/validate-skill/` - Validate skill entry

---

## 🔧 Utility Endpoints

### Data Export (GDPR)
- **GET** `/api/v1/profiles/export-data/` - Export user profile data

### Username Suggestions
- **GET** `/api/v1/profiles/username-suggestions/` - Get username suggestions

---

## 🔑 Social Authentication

### Social Auth
- **GET** `/auth/` - Social authentication endpoints (Django Social Auth)

---

## 🛡️ Admin Interface

### Django Admin
- **GET** `/admin/` - Django admin interface (development)

---

## 📝 Password Reset (Django Rest PasswordReset)

### Password Reset Integration
- **POST** `/api/v1/password-reset/` - Password reset endpoints

---

## 💡 Usage Examples

### Authentication Flow
```bash
# Register
POST http://127.0.0.1:8000/api/v1/users/auth/register/
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}

# Login
POST http://127.0.0.1:8000/api/v1/users/auth/login/
{
    "email": "john@example.com",
    "password": "securepass123"
}

# Get Profile
GET http://127.0.0.1:8000/api/v1/users/profile/
Authorization: Bearer <access_token>
```

### Profile Management
```bash
# Get my profile
GET /api/v1/profiles/my-profile/
Authorization: Bearer <access_token>

# Update profile
PATCH /api/v1/profiles/my-profile/
{
    "bio": "Updated bio",
    "phone_number": "+1234567890"
}
```

### Skills Management
```bash
# Add skill
POST /api/v1/profiles/my-skills/
{
    "name": "Python",
    "level": "advanced",
    "years_of_experience": 5
}
```

---

## 🔄 Response Formats

All endpoints return JSON responses with consistent structure:

### Success Response
```json
{
    "success": true,
    "data": { ... },
    "message": "Operation successful"
}
```

### Error Response
```json
{
    "success": false,
    "errors": { ... },
    "message": "Error description"
}
```

---

## 🔐 Authentication

Most endpoints require JWT authentication:
```
Authorization: Bearer <access_token>
```

Use the `/auth/login/` endpoint to obtain tokens.

---

## 📄 Pagination

List endpoints support pagination:
```
GET /api/v1/users/users/?page=1&page_size=20
```

Response includes pagination metadata:
```json
{
    "count": 100,
    "next": "http://127.0.0.1:8000/api/v1/users/users/?page=2",
    "previous": null,
    "results": [...]
}
```
