# AI Service Microservice

This is the AI Service microservice for the ClientNest platform, responsible for content generation, sentiment analysis, and AI-powered features.

## Features

- **Content Generation**: Generate social media content for multiple platforms
- **Sentiment Analysis**: Analyze text sentiment and emotions
- **Content Optimization**: Optimize content for better engagement
- **Hashtag Intelligence**: Suggest relevant hashtags
- **Performance Prediction**: Predict content performance
- **Cost Tracking**: Track AI API usage and costs
- **Template Management**: Manage reusable content templates

## Architecture

```
microservices/ai-service/
├── ai_service/           # Main Django project
├── common/              # Shared utilities and components
├── content_generation/  # Content generation service
├── sentiment_analysis/  # Sentiment analysis service
├── content_optimization/ # Content optimization service
├── ai_models/          # AI model configurations
└── requirements.txt    # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
cd microservices/ai-service
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `microservices/ai-service` directory:

```env
# Database
DB_NAME=ai_service_db
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432

# AI API Keys
DEEPSEEK_API_KEY=your-deepseek-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Service URLs
USER_SERVICE_URL=http://localhost:8001
CONTENT_SERVICE_URL=http://localhost:8002
SOCIAL_SERVICE_URL=http://localhost:8003
ANALYTICS_SERVICE_URL=http://localhost:8004

# Redis
REDIS_URL=redis://localhost:6379/3

# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run the Service

```bash
python manage.py runserver 8005
```

## API Endpoints

### Content Generation

- `POST /api/content/generate/` - Generate social media content
- `GET /api/content/content/` - List generated content
- `GET /api/content/content/{id}/` - Get specific content
- `GET /api/content/templates/` - List content templates
- `POST /api/content/templates/` - Create content template
- `GET /api/content/usage/` - List AI usage logs

### Legacy Endpoints (for backward compatibility)

- `POST /generate/` - Generate content
- `POST /sentiment/` - Analyze sentiment
- `POST /optimize/` - Optimize content
- `POST /hashtags/` - Get hashtag suggestions
- `POST /predict/` - Predict performance
- `GET /model-health/` - Check AI model health
- `GET /usage-stats/` - Get usage statistics

## Testing

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test content_generation.tests.test_logic

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Development

### Running Tests

```bash
cd microservices/ai-service
python -m pytest content_generation/test_logic.py -v
```

### Testing AI Service

```bash
# Start Django shell
python manage.py shell

# Test content generation
from ai_service.content_generation.logic import ContentGenerator
from ai_service.common.deepseek_client import DeepSeekClient

client = DeepSeekClient()
generator = ContentGenerator(client)

result = generator.generate_post(
    topic="AI in business",
    platform="linkedin",
    user=None,
    tone="professional"
)
print(result)
```

## Team Ownership

- **AI Team Lead**: Onyait Elias
- **AI Content Specialist**: Buwembo Denzel
- **AI Quality Assurance**: Biyo Stella

## Service Communication

This service communicates with other microservices:

- **User Service** (Port 8001): User authentication and profiles
- **Content Service** (Port 8002): Content management
- **Social Service** (Port 8003): Social media integration
- **Analytics Service** (Port 8004): Analytics and reporting

## Monitoring

- Health check: `GET /health/`
- Service status: `GET /model-health/`
- Usage statistics: `GET /usage-stats/`

## Deployment

The service is designed to run on port 8005 and can be deployed using:

- Docker containers
- Kubernetes orchestration
- AWS ECS/Fargate
- Traditional server deployment

## Cost Tracking

The service automatically tracks AI API usage and costs:

- Token usage (prompt, completion, total)
- Response times
- Cost per request
- User-specific usage logs

All usage data is stored in the `AIUsageLog` model for analytics and billing purposes. 