# Recommendation System Integration Guide

This guide provides step-by-step instructions for integrating the recommendation system into client-nest, including deployment, testing, and monitoring.

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- Python 3.8+ (for local development)
- PostgreSQL (if not using Docker)

### 2. Start the System
```bash
# Clone and navigate to project
cd client-nest

# Start all services
docker-compose up -d

# Check services are running
docker-compose ps
```

### 3. Initialize Database
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser (optional)
docker-compose exec backend python manage.py createsuperuser
```

## 📋 System Architecture

```
┌─────────────────┐    HTTP    ┌─────────────────┐
│   Frontend      │ ────────── │   Django        │
│   (React/Vue)   │            │   Backend       │
└─────────────────┘            └─────────────────┘
                                        │
                                        │ HTTP
                                        ▼
                               ┌─────────────────┐
                               │   ML Service    │
                               │   (FastAPI)     │
                               └─────────────────┘
```

## 🔧 Configuration

### Django Settings
Add to `backend/config/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'recommendations',
]

# ML Service Configuration
ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://localhost:8001')

# Recommendation Settings
RECOMMENDATION_CACHE_TTL = 3600
CHURN_PREDICTION_CACHE_TTL = 86400
```

### URL Configuration
Add to `backend/config/urls.py`:

```python
urlpatterns = [
    # ... existing URLs
    path('api/recommendations/', include('recommendations.urls')),
]
```

## 🧪 Testing the System

### 1. Test ML Service
```bash
# Check ML service health
curl http://localhost:8001/health

# Test recommendation endpoint
curl -X POST http://localhost:8001/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0, "algorithm": "hybrid", "top_k": 5}'

# Test churn prediction
curl -X POST http://localhost:8001/churn-predict \
  -H "Content-Type: application/json" \
  -d '{"user_id": 0, "features": {"recent_interactions": 5, "social_activity": ["facebook"], "ai_usage": {"total_requests": 10}}}'
```

### 2. Test Django API
```bash
# Get recommendations (requires authentication)
curl -X GET http://localhost:8000/api/recommendations/recommendations/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Log interaction
curl -X POST http://localhost:8000/api/recommendations/interactions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"interaction_type": "view", "content_id": "123", "content_type": "post"}'

# Get churn prediction
curl -X GET http://localhost:8000/api/recommendations/churn-prediction/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Python Testing
```python
# Test service directly
from recommendations.services import RecommendationService

service = RecommendationService()

# Log interaction
service.log_interaction(
    user_id=1,
    interaction_type='view',
    content_id='post_123',
    content_type='post'
)

# Get recommendations
recommendations = service.get_recommendations(
    user_id=1,
    algorithm='hybrid',
    top_k=5
)

# Predict churn
churn_risk = service.predict_churn(user_id=1)
```

## 📊 Monitoring and Analytics

### 1. Django Admin
Access admin at `http://localhost:8000/admin/` to view:
- User interactions
- Recommendations
- Churn predictions
- Performance metrics

### 2. ML Service Monitoring
- Health check: `http://localhost:8001/health`
- API docs: `http://localhost:8001/docs`
- OpenAPI spec: `http://localhost:8001/openapi.json`

### 3. Database Queries
```sql
-- Get user interaction statistics
SELECT 
    user_id,
    interaction_type,
    COUNT(*) as count
FROM recommendations_userinteraction
GROUP BY user_id, interaction_type;

-- Get recommendation performance
SELECT 
    algorithm,
    COUNT(*) as total_recommendations,
    SUM(CASE WHEN is_clicked THEN 1 ELSE 0 END) as clicks,
    AVG(CASE WHEN is_clicked THEN 1.0 ELSE 0.0 END) as ctr
FROM recommendations_recommendation
GROUP BY algorithm;

-- Get churn risk distribution
SELECT 
    CASE 
        WHEN churn_risk < 0.3 THEN 'low'
        WHEN churn_risk < 0.7 THEN 'medium'
        ELSE 'high'
    END as risk_level,
    COUNT(*) as user_count
FROM recommendations_churnprediction
GROUP BY risk_level;
```

## 🔄 Data Pipeline

### 1. User Interaction Flow
```
User Action → Frontend → Django API → UserInteraction Model → ML Service
```

### 2. Recommendation Flow
```
User Request → Django → Extract User Data → ML Service → Store & Return
```

### 3. Churn Prediction Flow
```
Scheduled Task → Extract Features → ML Service → Store Prediction
```

## 🚀 Production Deployment

### 1. Environment Variables
```bash
# Production settings
ML_SERVICE_URL=https://ml-service.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://redis:6379
DEBUG=False
SECRET_KEY=your-secret-key
```

### 2. Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Kubernetes Deployment
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-service
  template:
    metadata:
      labels:
        app: ml-service
    spec:
      containers:
      - name: ml-service
        image: your-registry/ml-service:latest
        ports:
        - containerPort: 8000
```

## 🔧 Troubleshooting

### Common Issues

#### 1. ML Service Not Responding
```bash
# Check if service is running
docker-compose ps ml-service

# Check logs
docker-compose logs ml-service

# Restart service
docker-compose restart ml-service
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose ps db

# Check Django database connection
docker-compose exec backend python manage.py dbshell
```

#### 3. Recommendation Quality Issues
- Check user interaction data quality
- Verify ML service is receiving correct data
- Monitor recommendation feedback
- Adjust algorithm parameters

#### 4. Performance Issues
- Enable caching for recommendations
- Optimize database queries
- Use async processing for heavy operations
- Monitor ML service response times

### Debug Commands
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# Access Django shell
docker-compose exec backend python manage.py shell

# Access ML service container
docker-compose exec ml-service bash

# Check database
docker-compose exec db psql -U postgres -d clientnest
```

## 📈 Performance Optimization

### 1. Caching Strategy
```python
# Cache recommendations
from django.core.cache import cache

def get_cached_recommendations(user_id, algorithm):
    cache_key = f"recommendations:{user_id}:{algorithm}"
    recommendations = cache.get(cache_key)
    
    if not recommendations:
        recommendations = service.get_recommendations(user_id, algorithm)
        cache.set(cache_key, recommendations, 3600)  # 1 hour
    
    return recommendations
```

### 2. Database Optimization
```python
# Use select_related for foreign keys
recommendations = Recommendation.objects.select_related('user').filter(user=user)

# Use prefetch_related for many-to-many
interactions = UserInteraction.objects.prefetch_related('user').filter(user=user)
```

### 3. Async Processing
```python
# Use Celery for heavy operations
from celery import shared_task

@shared_task
def update_user_recommendations(user_id):
    service = RecommendationService()
    recommendations = service.get_recommendations(user_id)
    # Store recommendations asynchronously
```

## 🔒 Security Considerations

### 1. Authentication
- All API endpoints require authentication
- Use JWT tokens for stateless authentication
- Implement rate limiting

### 2. Data Privacy
- Anonymize user data for ML training
- Implement data retention policies
- Comply with GDPR/privacy regulations

### 3. Input Validation
- Validate all API inputs
- Sanitize user data
- Prevent SQL injection and XSS

## 📚 Next Steps

### 1. Advanced Features
- A/B testing for recommendations
- Real-time personalization
- Multi-armed bandit algorithms
- Deep learning models

### 2. Monitoring
- Set up Prometheus/Grafana
- Implement alerting
- Track business metrics

### 3. Scaling
- Horizontal scaling of ML service
- Database sharding
- CDN for static content

## 🤝 Team Collaboration

### Backend Team
- Monitor API performance
- Optimize database queries
- Implement caching strategies
- Handle data pipeline issues

### Frontend Team
- Integrate recommendation APIs
- Implement user interaction tracking
- Design recommendation UI components
- A/B test recommendation placements

### ML Team
- Improve recommendation algorithms
- Monitor model performance
- Retrain models with new data
- Optimize inference speed

### DevOps Team
- Deploy and monitor services
- Set up CI/CD pipelines
- Manage infrastructure scaling
- Implement monitoring and alerting

---

For additional support, refer to:
- [ML Service Documentation](ml_service/README.md)
- [Recommendations App Documentation](backend/recommendations/README.md)
- [API Documentation](http://localhost:8001/docs)
- [Django Admin](http://localhost:8000/admin/) 