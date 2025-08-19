# AI Service Endpoints Documentation

## Overview

The AI Service provides intelligent content generation, sentiment analysis, hashtag optimization, and optimal posting time suggestions for social media management. All endpoints are available on port 8005.

## Base URL
```
http://localhost:8005
```

## Authentication
Currently, all endpoints use `AllowAny` permissions for testing. In production, these should be secured with proper authentication.

## Endpoints

### 1. Content Generation
**POST** `/api/ai/generate/content/`

Generate social media content using AI.

**Request Body:**
```json
{
  "topic": "Productivity tips for remote workers",
  "platform": "linkedin",
  "tone": "professional",
  "batch": false
}
```

**Response:**
```json
{
  "content": "🚀 Boost your remote work productivity with these proven strategies...",
  "hashtags": ["#remotework", "#productivity", "#workfromhome"],
  "quality_score": 0.92,
  "safety_check": "passed",
  "readability_score": 0.85,
  "engagement_prediction": 0.78,
  "optimal_posting_time_suggestion": "2024-01-16T09:00:00Z"
}
```

### 2. Sentiment Analysis
**POST** `/api/ai/analyze/sentiment/`

Analyze the sentiment of text content.

**Request Body:**
```json
{
  "text": "I love this product! It's amazing and works perfectly.",
  "batch": false
}
```

**Response:**
```json
{
  "sentiment": "positive",
  "confidence": 0.95,
  "scores": {
    "positive": 0.95,
    "negative": 0.02,
    "neutral": 0.03
  },
  "emotions": ["joy", "satisfaction"]
}
```

### 3. Hashtag Optimization ⭐ NEW
**POST** `/api/ai/optimize/hashtags/`

Optimize hashtags for social media content to maximize engagement.

**Request Body:**
```json
{
  "content": "Excited to announce our new AI-powered social media management platform! 🚀 We're helping businesses create engaging content, analyze performance, and optimize their social media strategy.",
  "platform": "linkedin",
  "target_audience": "professionals",
  "industry": "technology"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hashtags": [
      {
        "tag": "#socialmediamanagement",
        "category": "niche",
        "estimated_reach": "high",
        "engagement_potential": "high"
      },
      {
        "tag": "#AI",
        "category": "trending",
        "estimated_reach": "high",
        "engagement_potential": "high"
      },
      {
        "tag": "#digitalmarketing",
        "category": "popular",
        "estimated_reach": "medium",
        "engagement_potential": "medium"
      }
    ],
    "strategy": {
      "platform_specific": "LinkedIn favors professional hashtags",
      "audience_targeting": "Focus on B2B and professional development",
      "trending_opportunities": "AI and automation are trending topics"
    },
    "recommendations": [
      "Use a mix of popular and niche hashtags",
      "Include industry-specific hashtags",
      "Monitor trending hashtags regularly"
    ]
  },
  "usage": {
    "tokens_consumed": 234,
    "cost": 0.0018
  }
}
```

### 4. Optimal Posting Time Suggestion ⭐ NEW
**POST** `/api/ai/schedule/optimal/`

Suggest optimal posting times for social media content based on platform and audience.

**Request Body:**
```json
{
  "platform": "instagram",
  "content_type": "post",
  "target_audience": "millennials",
  "timezone": "America/New_York",
  "industry": "fashion"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "optimal_times": {
      "monday": ["09:00", "12:00", "18:00"],
      "tuesday": ["09:00", "12:00", "18:00"],
      "wednesday": ["09:00", "12:00", "18:00"],
      "thursday": ["09:00", "12:00", "18:00"],
      "friday": ["09:00", "12:00", "18:00"],
      "saturday": ["10:00", "14:00", "19:00"],
      "sunday": ["10:00", "14:00", "19:00"]
    },
    "platform_strategy": {
      "best_days": ["monday", "wednesday", "friday"],
      "best_hours": ["09:00-11:00", "12:00-14:00", "18:00-20:00"],
      "audience_peak_times": "Peak engagement during business hours and evening",
      "engagement_patterns": "Higher engagement on weekdays during business hours"
    },
    "recommendations": [
      "Post during peak business hours (9 AM - 11 AM)",
      "Engage during lunch hours (12 PM - 2 PM)",
      "Post during evening hours (6 PM - 8 PM)",
      "Avoid posting during weekends unless targeting specific audience"
    ],
    "timezone_considerations": "All times are in America/New_York timezone"
  },
  "usage": {
    "tokens_consumed": 156,
    "cost": 0.0012
  }
}
```

### 5. Model Health Status
**GET** `/api/ai/models/status/`

Check the health status of AI models.

**Response:**
```json
{
  "status": "healthy",
  "models": {
    "deepseek-chat": "available",
    "deepseek-coder": "available"
  }
}
```

### 6. Usage Statistics
**GET** `/api/ai/usage/stats/`

Get usage statistics for the AI service.

**Response:**
```json
{
  "total_tasks": 156,
  "completed_tasks": 150,
  "failed_tasks": 6,
  "success_rate": 0.96
}
```

### 7. Token Usage
**GET** `/api/ai/token/usage/`

Get current token usage and budget status.

**Response:**
```json
{
  "token_usage": {
    "daily_usage": 45230,
    "daily_limit": 100000,
    "daily_percentage": 0.45,
    "total_usage": 125000,
    "total_budget": 500000,
    "total_percentage": 0.25
  },
  "budget_warnings": [],
  "remaining_daily": 54770,
  "remaining_total": 375000,
  "estimated_cost": 0.125
}
```

## Error Handling

All endpoints return standard HTTP status codes:

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request data
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: AI service unavailable

**Error Response Format:**
```json
{
  "error": "Error message description"
}
```

## Testing

Use the provided test script to verify all endpoints:

```bash
cd microservices/ai-service
python test_new_endpoints.py
```

## Architecture Compliance

✅ **Implemented Endpoints:**
- `POST /api/ai/generate/content` - Content generation
- `POST /api/ai/analyze/sentiment` - Sentiment analysis
- `POST /api/ai/optimize/hashtags` - Hashtag optimization ⭐ NEW
- `POST /api/ai/schedule/optimal` - Optimal posting time ⭐ NEW
- `GET /api/ai/models/status` - Model health status

All required AI service endpoints from the architecture specification are now implemented and functional.

## Integration Notes

- **Content Service Integration**: Generated content can be saved to the content service
- **Analytics Service Integration**: Usage statistics are tracked for analytics
- **Social Service Integration**: Optimized hashtags and posting times can be used for social media publishing
- **User Service Integration**: User preferences and team settings can influence AI recommendations

## Performance Considerations

- **Response Time**: AI endpoints typically respond within 2-5 seconds
- **Rate Limiting**: Consider implementing rate limiting for production use
- **Caching**: Generated content and hashtag suggestions can be cached
- **Batch Processing**: Use `batch: true` for processing multiple items asynchronously

## Security Considerations

- **Authentication**: Implement proper JWT authentication
- **Input Validation**: All user inputs are validated
- **Content Filtering**: Generated content is checked for safety
- **Usage Limits**: Token usage is tracked and limited 