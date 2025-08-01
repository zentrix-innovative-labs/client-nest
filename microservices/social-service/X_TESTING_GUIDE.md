# X Service Testing Guide

This guide will help you test the X (Twitter) service to ensure it's working properly.

## Prerequisites

1. **X API Credentials**: You need valid X API credentials
   - `X_API_KEY` - Your X API key
   - `X_API_SECRET` - Your X API secret
   - `X_TEST_ACCESS_TOKEN` - A valid access token for testing
   - `X_TEST_ACCESS_TOKEN_SECRET` - The corresponding access token secret

2. **Environment Setup**: Make sure your environment variables are set

## Testing Methods

### Method 1: Direct Service Testing

Test the X service directly using the simple test script:

```bash
cd client-nest-update/microservices/social-service

# Set environment variables
export X_TEST_ACCESS_TOKEN="your_access_token"
export X_TEST_ACCESS_TOKEN_SECRET="your_access_token_secret"

# Run the test
python simple_x_test.py
```

### Method 2: Django Management Command

Test using Django's management command system:

```bash
cd client-nest-update/microservices/social-service

# Set environment variables
export X_TEST_ACCESS_TOKEN="your_access_token"
export X_TEST_ACCESS_TOKEN_SECRET="your_access_token_secret"

# Run the management command
python manage.py test_x_service

# Or with custom content
python manage.py test_x_service --post-content "Custom test tweet! 🎯"

# Skip posting test
python manage.py test_x_service --skip-posting
```

### Method 3: API Endpoint Testing

Test the REST API endpoints:

```bash
cd client-nest-update/microservices/social-service

# Set environment variables
export API_TOKEN="your_jwt_token"
export API_BASE_URL="http://localhost:8000"

# Run the API test
python test_x_api.py
```

### Method 4: Manual API Testing

Test the endpoints manually using curl or Postman:

#### Test Connection
```bash
curl -X GET "http://localhost:8000/api/social/x/test-connection/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Test Posting
```bash
curl -X POST "http://localhost:8000/api/social/x/test-post/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test tweet from curl! 🚀"}'
```

#### Check Account Status
```bash
curl -X GET "http://localhost:8000/api/social/accounts/status/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Expected Results

### Successful Test Output

```
🧪 Testing X Service...
1. Checking configuration...
✅ Configuration OK
2. Testing service initialization...
✅ Service initialized
3. Testing account info...
✅ Account info retrieved
   User: @yourusername (Your Name)
4. Testing content posting...
✅ Content posted successfully
   Tweet ID: 1234567890123456789

✅ X Service test completed!
```

### Common Issues and Solutions

#### 1. Configuration Issues
- **Problem**: `X_API_KEY` or `X_API_SECRET` not found
- **Solution**: Check your `.env` file and ensure the variables are set correctly

#### 2. Authentication Issues
- **Problem**: "Authentication required" or "No active X account found"
- **Solution**: 
  - Ensure you have valid access tokens
  - Check that the user has an active X account in the database
  - Verify JWT token is valid for API testing

#### 3. API Rate Limiting
- **Problem**: "Rate limit exceeded"
- **Solution**: Wait before running tests again, or use different test accounts

#### 4. Network Issues
- **Problem**: "Request failed" or connection errors
- **Solution**: Check your internet connection and X API availability

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `X_API_KEY` | X API key | Yes |
| `X_API_SECRET` | X API secret | Yes |
| `X_TEST_ACCESS_TOKEN` | Test access token | For direct testing |
| `X_TEST_ACCESS_TOKEN_SECRET` | Test access token secret | For direct testing |
| `API_TOKEN` | JWT token for API testing | For API testing |
| `API_BASE_URL` | Base URL for API testing | For API testing |

## Troubleshooting

### Check Configuration
```bash
# Verify environment variables are loaded
python -c "import os; from social_service.Social_media_platforms.x_config import X_CONFIG; print('API_KEY:', 'Set' if X_CONFIG['API_KEY'] else 'Not set')"
```

### Check Database
```bash
# Check if X accounts exist in database
python manage.py shell
```
```python
from social_service.Social_media_platforms.models import SocialAccount
accounts = SocialAccount.objects.filter(platform='x', is_active=True)
print(f"Active X accounts: {accounts.count()}")
```

### Check Logs
```bash
# Check Django logs for errors
tail -f logs/django.log
```

## Security Notes

- Never commit API credentials to version control
- Use test accounts for testing, not production accounts
- Rotate test credentials regularly
- Monitor API usage to avoid rate limiting

## Next Steps

After successful testing:

1. **Integration Testing**: Test the service with your frontend application
2. **Load Testing**: Test with multiple concurrent requests
3. **Error Handling**: Test various error scenarios
4. **Media Upload**: Test image/video upload functionality if needed

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the X API documentation
3. Check Django logs for detailed error messages
4. Verify your X API credentials and permissions 