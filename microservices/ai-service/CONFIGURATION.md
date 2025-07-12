# AI Service Configuration Guide

## Environment Variables

This service uses environment variables for all configuration. Create a `.env` file in the root directory with the following variables:

### Required Variables

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# AI Model Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### Optional Variables

```bash
# AI Model Settings
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=4000
DEEPSEEK_TEMPERATURE=0.7

# Fallback AI Models
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Token Budget Settings
TOKEN_BUDGET_TOTAL=1000000
TOKEN_BUDGET_DAILY=50000
TOKEN_BUDGET_REQUEST_LIMIT=2000

# Service URLs
USER_SERVICE_URL=http://localhost:8001
CONTENT_SERVICE_URL=http://localhost:8002
# ... other service URLs
```

## Security Best Practices

1. **Never commit `.env` files** - They are excluded in `.gitignore`
2. **Use strong, unique secret keys** - Generate using `python -c "import secrets; print(secrets.token_urlsafe(50))"`
3. **Use different configurations for different environments** - Development, staging, production
4. **Rotate API keys regularly** - Especially for production environments
5. **Use environment-specific databases** - Separate databases for dev/staging/prod

## Setup Instructions

1. Copy `.env.example` to `.env`
2. Fill in your actual values
3. Never commit the `.env` file
4. Use different `.env` files for different environments

## Validation

The application validates required configuration on startup. Missing required variables will cause the application to fail with a clear error message. 