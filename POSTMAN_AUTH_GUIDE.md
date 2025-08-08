# 🔐 Postman Authentication Guide for ClientNest User Service

## 📋 Quick Reference

### Base URL: `http://127.0.0.1:8000`

---

## 🎯 Authentication Requirements by Endpoint

### 🟢 **No Authentication Required** (Public Endpoints)
- `POST /api/v1/users/auth/register/` - User registration
- `POST /api/v1/users/auth/login/` - User login  
- `GET /api/v1/users/auth/verify-email/<uidb64>/<token>/` - Email verification
- `POST /api/v1/users/auth/resend-verification/` - Resend verification
- `POST /api/v1/users/auth/reset-password/` - Request password reset
- `POST /api/v1/users/auth/reset-password/<uidb64>/<token>/` - Confirm password reset
- `GET /` - Service info
- `GET /health/` - Health check

### 🟡 **User Authentication Required** (JWT Token)
- `GET /api/v1/users/profile/` - Get current user profile
- `PUT /api/v1/users/profile/` - Update current user profile
- `PATCH /api/v1/users/profile/` - Partially update profile
- `POST /api/v1/users/auth/logout/` - User logout
- `POST /api/v1/users/auth/change-password/` - Change password
- `POST /api/v1/users/auth/refresh/` - Refresh JWT token

### 🔴 **Admin Authentication Required** (Admin JWT Token)
- `GET /api/v1/users/users/` - List all users
- `POST /api/v1/users/users/` - Create new user
- `GET /api/v1/users/users/{id}/` - Get specific user details
- `PUT /api/v1/users/users/{id}/` - Update user (full)
- `PATCH /api/v1/users/users/{id}/` - Update user (partial)
- `DELETE /api/v1/users/users/{id}/` - Delete user

---

## 🚀 Step-by-Step Postman Setup

### Step 1: Get JWT Token (Login)

1. **Create New Request**
   - Method: `POST`
   - URL: `http://127.0.0.1:8000/api/v1/users/auth/login/`

2. **Set Headers**
   ```
   Content-Type: application/json
   ```

3. **Set Body** (raw JSON)
   ```json
   {
       "email": "test@example.com",
       "password": "securepass123"
   }
   ```

4. **Send Request** - You'll get response like:
   ```json
   {
       "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "user": {
           "id": "1ee0e0c6-a42a-4ea3-9643-4157226369f2",
           "email": "test@example.com",
           "username": "testuser123"
       }
   }
   ```

5. **Copy the `access` token** for use in authenticated requests

### Step 2: Use JWT Token in Authenticated Requests

1. **Create New Request** for user endpoints
   - Method: `GET` (or whatever method you need)
   - URL: `http://127.0.0.1:8000/api/v1/users/users/` (for admin endpoints)

2. **Set Authorization Header**
   - Go to **Headers** tab
   - Add header:
     ```
     Key: Authorization
     Value: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     ```
   
   **OR** Use Postman's **Authorization** tab:
   - Type: `Bearer Token`
   - Token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

---

## 🛠️ Quick Test Examples

### Test 1: Register a New User (No Auth Required)
```
POST http://127.0.0.1:8000/api/v1/users/auth/register/
Content-Type: application/json

{
    "username": "postmanuser",
    "email": "postman@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "Postman",
    "last_name": "Tester"
}
```

### Test 2: Login and Get Token (No Auth Required)
```
POST http://127.0.0.1:8000/api/v1/users/auth/login/
Content-Type: application/json

{
    "email": "postman@example.com",
    "password": "securepass123"
}
```

### Test 3: Get Current User Profile (User Auth Required)
```
GET http://127.0.0.1:8000/api/v1/users/profile/
Authorization: Bearer <your_access_token_here>
```

### Test 4: List All Users (Admin Auth Required)
```
GET http://127.0.0.1:8000/api/v1/users/users/
Authorization: Bearer <admin_access_token_here>
```

---

## 🔧 Creating Admin User for Testing

To test admin endpoints, you need an admin user:

### Option 1: Create via Django Command
```bash
cd microservices/user-service
python manage.py createsuperuser
```

### Option 2: Make Existing User Admin
1. Register a normal user
2. Access Django admin: `http://127.0.0.1:8000/admin/`
3. Login with superuser credentials
4. Edit the user and check "Staff status" and "Superuser status"

---

## ⚡ Postman Collection Variables

Set up environment variables in Postman:

1. **Create Environment** (Settings > Environments)
2. **Add Variables**:
   ```
   base_url: http://127.0.0.1:8000
   access_token: (leave empty, will be set after login)
   ```

3. **Use Variables in Requests**:
   - URL: `{{base_url}}/api/v1/users/users/`
   - Authorization: `Bearer {{access_token}}`

---

## 🚨 Common Issues & Solutions

### Issue: "Authentication credentials were not provided"
**Solution**: Add the Authorization header with Bearer token

### Issue: "You do not have permission to perform this action"
**Solution**: 
- For user endpoints: Use regular user token
- For admin endpoints: Use admin/superuser token

### Issue: "Token is invalid or expired"
**Solution**: 
1. Use the refresh token to get a new access token
2. Or login again to get new tokens

### Refresh Token Example:
```
POST http://127.0.0.1:8000/api/v1/users/auth/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token_here"
}
```

---

## 📝 Token Lifespan

- **Access Token**: 1 hour (for API requests)
- **Refresh Token**: 7 days (to get new access tokens)

Always store both tokens and use refresh when access token expires!

---

## 🎯 Testing Workflow

1. **Register** a new user → Get user credentials
2. **Login** with credentials → Get JWT tokens  
3. **Test user endpoints** with access token
4. **Create admin user** (via Django command)
5. **Login as admin** → Get admin JWT tokens
6. **Test admin endpoints** with admin access token

Happy testing! 🚀
