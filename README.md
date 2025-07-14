# ClientNest - AI-Powered Social Media Management Platform

A production-ready social media management platform with AI-powered content generation using DeepSeek API via OpenRouter.

## Features

- 🤖 **AI Content Generation**: Generate engaging social media posts using DeepSeek AI
- 📊 **Usage Analytics**: Track AI usage, costs, and performance metrics
- 🔐 **Secure Authentication**: JWT-based authentication with proper permissions
- 📈 **Cost Management**: Monitor and control AI API costs by user/tier
- 🚀 **Production Ready**: Robust error handling, logging, and monitoring

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- OpenRouter API key (free tier available)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd client_nest
   ```

2. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your configuration
   DJANGO_SECRET_KEY=your-secret-key-here
   OPENROUTER_API_KEY=your-openrouter-api-key
   POSTGRES_DB=client-nest
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   cd backend
   python -m venv venv  # Or use python -m venv .venv for consistency
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Copy the example env file and edit as needed
   # Edit .env with your configuration (see below for required variables)
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

#### Required Environment Variables
The backend requires a `.env` file in the `backend/` directory. You can copy `backend/.env.example` and fill in your values. The following variables are required:

| Variable              | Description                                 |
|-----------------------|---------------------------------------------|
| DJANGO_SECRET_KEY     | Django secret key (required)                |
| POSTGRES_DB           | Postgres database name                      |
| POSTGRES_USER         | Postgres username                           |
| POSTGRES_PASSWORD     | Postgres password                           |
| POSTGRES_HOST         | Postgres host (default: localhost)          |
| POSTGRES_PORT         | Postgres port (default: 5432)               |
| EMAIL_HOST            | SMTP server host                            |
| EMAIL_PORT            | SMTP server port                            |
| EMAIL_USE_TLS         | Use TLS for email (True/False)              |
| EMAIL_USE_SSL         | Use SSL for email (True/False)              |
| EMAIL_HOST_USER       | SMTP username                               |
| EMAIL_HOST_PASSWORD   | SMTP password                               |
| DEFAULT_FROM_EMAIL    | Default from email address                  |
| FACEBOOK_APP_ID       | Facebook App ID (optional)                  |
| FACEBOOK_APP_SECRET   | Facebook App Secret (optional)              |
| FACEBOOK_REDIRECT_URI | Facebook Redirect URI (optional)            |

3. **Frontend Setup**
   ```bash
   # The frontend directory is not present in this repository. If/when it is added, follow the instructions in that directory.
   ```

### Standalone Test

Test the DeepSeek client without Django:

> **Note:** If you wish to use Docker Compose for Postgres/Redis, ensure a `docker-compose.yml` file is present. If not, you must install and run Postgres and Redis manually.

```bash
# Set your API key
$env:OPENROUTER_API_KEY="your-api-key"

# Run the test script
python test_deepseek_client.py
```

### Django Integration Test

Test the AI integration with Django:

```bash
cd backend
python manage.py shell

# In the Django shell:
from ai_services.common.deepseek_client import DeepSeekClient
client = DeepSeekClient()
result = client.generate_content(
    system_prompt="You are a helpful assistant.",
    user_prompt="Write a short post about AI.",
    user=None
)
print(result)
```

## API Endpoints

### AI Content Generation

**POST** `/api/ai/generate/`

Generate AI content with authentication and validation.

```json
{
  "system_prompt": "You are a social media expert.",
  "user_prompt": "Write a LinkedIn post about AI trends",
  "temperature": 0.8,
  "max_tokens": 200
}
```

**Response:**
```json
{
  "success": true,
  "content": "Generated content here...",
  "model": "deepseek/deepseek-r1-0528:free",
  "parameters": {
    "temperature": 0.8,
    "max_tokens": 200
  }
}
```

### Health Check

**GET** `/api/ai/health/`

Check AI service status.

### Usage Statistics

**GET** `/api/ai/usage/`

Get AI usage statistics for the authenticated user.

## Configuration

### AI Settings

The AI configuration is in `backend/config/settings.py`:

```python
# DeepSeek API pricing (per 1,000 tokens)
DEEPSEEK_PRICING = {
    'prompt': 0.0014,      # $0.0014 per 1K prompt tokens
    'completion': 0.0028,  # $0.0028 per 1K completion tokens
}

# AI usage limits by subscription tier
AI_USAGE_LIMITS = {
    'free': {
        'content_generation': 5,
        'sentiment_analysis': 10,
        'total_tokens': 5000,
    },
    # ... other tiers
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key | Yes |
| `POSTGRES_DB` | Database name | Yes |
| `POSTGRES_USER` | Database user | Yes |
| `POSTGRES_PASSWORD` | Database password | Yes |
| `POSTGRES_HOST` | Database host | Yes |
| `POSTGRES_PORT` | Database port | Yes |

## Project Structure

```
client_nest/
├── ai_services/                 # AI services package
│   └── common/
│       ├── __init__.py
│       ├── deepseek_client.py   # Main AI client
│       └── signals.py           # Django signals
├── backend/                     # Django backend
│   ├── config/                  # Django settings
│   ├── ai_integration/          # AI integration app
│   │   ├── models.py           # AI usage models
│   │   ├── views.py            # API views
│   │   ├── signals.py          # Usage tracking
│   │   └── urls.py             # URL patterns
│   └── manage.py
├── test_deepseek_client.py     # Standalone test script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Error Handling

The AI client includes comprehensive error handling:

- **AIClientError**: Base exception for AI client errors
- **AIAPIError**: Errors returned by the AI API
- **AIConnectionError**: Connection/network errors

All errors are logged and return appropriate HTTP status codes.

## Security Features

- ✅ JWT authentication required for all AI endpoints
- ✅ Input validation and sanitization
- ✅ Rate limiting and usage tracking
- ✅ Secure API key management
- ✅ CSRF protection enabled

## Monitoring and Logging

- **Usage Tracking**: All AI requests are logged with costs