# ClientNest API Design

## API Architecture Overview

ClientNest uses a **RESTful API architecture** with the following principles:

- **REST-compliant**: Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **JSON-first**: All requests and responses use JSON format
- **Stateless**: Each request contains all necessary information
- **Versioned**: API versioning through URL path (`/api/v1/`)
- **Secure**: JWT-based authentication with role-based access control

## API Structure Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API ARCHITECTURE                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Load Balancer │    │   API Gateway   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ React Frontend  │────│ AWS ALB         │────│ AWS API Gateway │
│ Mobile Apps     │    │ Health Checks   │    │ Rate Limiting   │
│ Third-party     │    │ SSL Termination │    │ Authentication  │
│ Integrations    │    │ Request Routing │    │ Request Logging │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            MICROSERVICES LAYER                                 │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Auth Service  │  User Service   │ Social Service  │    AI Service           │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ /api/v1/auth/   │ /api/v1/users/  │ /api/v1/social/ │ /api/v1/ai/             │
│ - login         │ - profile       │ - accounts      │ - generate-content      │
│ - register      │ - teams         │ - posts         │ - analyze-sentiment     │
│ - refresh       │ - preferences   │ - comments      │ - optimize-content      │
│ - logout        │ - notifications │ - scheduling    │ - usage-tracking        │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                        │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │     Redis       │   TimescaleDB   │       AWS S3            │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ Primary Data    │ Cache & Session │ Analytics Data  │ Media Storage           │
│ User Accounts   │ Rate Limiting   │ Time Series     │ File Uploads            │
│ Posts & Content │ Temp Data       │ Metrics         │ Backups                 │
│ Relationships   │ Queue Jobs      │ Events          │ Static Assets           │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## Authentication & Authorization

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "team_id": "660f9500-f39c-52e5-b827-557766551111",
    "role": "admin",
    "permissions": ["read:posts", "write:posts", "manage:team"],
    "iat": 1640995200,
    "exp": 1641081600
  }
}
```

### Authentication Endpoints

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "timezone": "America/New_York"
}

Response 201:
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "email_verified": false
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    }
  }
}
```

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response 200:
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "teams": [
        {
          "id": "660f9500-f39c-52e5-b827-557766551111",
          "name": "My Team",
          "role": "owner"
        }
      ]
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 3600
    }
  }
}
```

```http
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer {refresh_token}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

## User Management API

### User Profile Endpoints

```http
GET /api/v1/users/profile
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://s3.amazonaws.com/avatars/user123.jpg",
    "timezone": "America/New_York",
    "email_verified": true,
    "created_at": "2024-01-15T10:30:00Z",
    "preferences": {
      "notifications": {
        "email": true,
        "push": false
      },
      "theme": "light",
      "language": "en"
    }
  }
}
```

```http
PUT /api/v1/users/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "timezone": "America/Los_Angeles",
  "preferences": {
    "notifications": {
      "email": false,
      "push": true
    },
    "theme": "dark"
  }
}

Response 200:
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "timezone": "America/Los_Angeles",
    "updated_at": "2024-01-15T11:45:00Z"
  }
}
```

### Team Management Endpoints

```http
GET /api/v1/teams
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "teams": [
      {
        "id": "660f9500-f39c-52e5-b827-557766551111",
        "name": "My Marketing Team",
        "role": "owner",
        "plan_type": "professional",
        "member_count": 5,
        "created_at": "2024-01-10T09:00:00Z"
      },
      {
        "id": "770f9500-f39c-52e5-b827-557766552222",
        "name": "Client Project",
        "role": "editor",
        "plan_type": "business",
        "member_count": 12,
        "created_at": "2024-01-12T14:30:00Z"
      }
    ],
    "pagination": {
      "total": 2,
      "page": 1,
      "per_page": 20
    }
  }
}
```

```http
POST /api/v1/teams
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "New Marketing Team",
  "plan_type": "starter"
}

Response 201:
{
  "success": true,
  "data": {
    "id": "880f9500-f39c-52e5-b827-557766553333",
    "name": "New Marketing Team",
    "plan_type": "starter",
    "owner_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-01-15T12:00:00Z"
  }
}
```

## Social Media API

### Social Account Management

```http
GET /api/v1/social/accounts
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111

Response 200:
{
  "success": true,
  "data": {
    "accounts": [
      {
        "id": "990f9500-f39c-52e5-b827-557766554444",
        "platform": "facebook",
        "username": "mycompany",
        "platform_id": "123456789",
        "is_active": true,
        "permissions": ["publish_posts", "read_insights"],
        "connected_at": "2024-01-10T10:00:00Z"
      },
      {
        "id": "aa0f9500-f39c-52e5-b827-557766555555",
        "platform": "instagram",
        "username": "mycompany_ig",
        "platform_id": "987654321",
        "is_active": true,
        "permissions": ["publish_posts", "read_insights"],
        "connected_at": "2024-01-11T15:30:00Z"
      }
    ]
  }
}
```

```http
POST /api/v1/social/accounts/connect
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111
Content-Type: application/json

{
  "platform": "twitter",
  "oauth_code": "abc123def456",
  "redirect_uri": "https://app.clientnest.com/connect/callback"
}

Response 201:
{
  "success": true,
  "data": {
    "id": "bb0f9500-f39c-52e5-b827-557766556666",
    "platform": "twitter",
    "username": "mycompany_tw",
    "platform_id": "555666777",
    "is_active": true,
    "permissions": ["publish_posts", "read_mentions"],
    "connected_at": "2024-01-15T12:30:00Z"
  }
}
```

### Post Management

```http
GET /api/v1/social/posts
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111

Query Parameters:
- status: draft|scheduled|published|failed
- platform: facebook|instagram|twitter|linkedin
- page: 1
- per_page: 20
- sort: created_at|scheduled_at|published_at
- order: asc|desc

Response 200:
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "cc0f9500-f39c-52e5-b827-557766557777",
        "title": "New Product Launch",
        "content": "Excited to announce our new product! 🚀 #innovation #startup",
        "hashtags": ["#innovation", "#startup"],
        "status": "published",
        "platforms": ["facebook", "instagram"],
        "scheduled_at": "2024-01-15T09:00:00Z",
        "published_at": "2024-01-15T09:00:15Z",
        "ai_generated": true,
        "engagement": {
          "likes": 45,
          "comments": 12,
          "shares": 8,
          "reach": 1250
        },
        "media": [
          {
            "id": "dd0f9500-f39c-52e5-b827-557766558888",
            "type": "image",
            "url": "https://s3.amazonaws.com/media/post123.jpg",
            "alt_text": "Product showcase image"
          }
        ],
        "created_at": "2024-01-14T16:30:00Z",
        "updated_at": "2024-01-15T09:00:15Z"
      }
    ],
    "pagination": {
      "total": 156,
      "page": 1,
      "per_page": 20,
      "total_pages": 8
    }
  }
}
```

```http
POST /api/v1/social/posts
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111
Content-Type: application/json

{
  "title": "Weekend Motivation",
  "content": "Start your week with positive energy! What are your goals for this week?",
  "hashtags": ["#motivation", "#mondayvibes", "#goals"],
  "platforms": ["facebook", "instagram", "linkedin"],
  "scheduled_at": "2024-01-22T08:00:00Z",
  "timezone": "America/New_York",
  "media_ids": ["ee0f9500-f39c-52e5-b827-557766559999"]
}

Response 201:
{
  "success": true,
  "data": {
    "id": "ff0f9500-f39c-52e5-b827-557766560000",
    "title": "Weekend Motivation",
    "content": "Start your week with positive energy! What are your goals for this week?",
    "hashtags": ["#motivation", "#mondayvibes", "#goals"],
    "status": "scheduled",
    "platforms": ["facebook", "instagram", "linkedin"],
    "scheduled_at": "2024-01-22T08:00:00Z",
    "created_at": "2024-01-15T13:00:00Z"
  }
}
```

### Comment Management

```http
GET /api/v1/social/comments
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111

Query Parameters:
- account_id: 990f9500-f39c-52e5-b827-557766554444
- status: new|replied|ignored|flagged
- sentiment: positive|negative|neutral
- priority: high|medium|low
- page: 1
- per_page: 50

Response 200:
{
  "success": true,
  "data": {
    "comments": [
      {
        "id": "110f9500-f39c-52e5-b827-557766561111",
        "account_id": "990f9500-f39c-52e5-b827-557766554444",
        "platform": "facebook",
        "platform_id": "comment_123456",
        "content": "Love this product! When will it be available in Europe?",
        "author_name": "Sarah Johnson",
        "author_id": "user_789012",
        "sentiment": "positive",
        "priority": "high",
        "status": "new",
        "created_at": "2024-01-15T10:45:00Z",
        "metadata": {
          "post_id": "post_456789",
          "location": "London, UK"
        }
      }
    ],
    "pagination": {
      "total": 89,
      "page": 1,
      "per_page": 50,
      "total_pages": 2
    },
    "summary": {
      "new_comments": 23,
      "high_priority": 5,
      "sentiment_breakdown": {
        "positive": 45,
        "negative": 12,
        "neutral": 32
      }
    }
  }
}
```

```http
POST /api/v1/social/comments/{comment_id}/respond
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111
Content-Type: application/json

{
  "content": "Hi Sarah! Thanks for your interest. We're planning to launch in Europe Q2 2024. Stay tuned for updates! 🌍",
  "ai_generated": false
}

Response 201:
{
  "success": true,
  "data": {
    "response_id": "220f9500-f39c-52e5-b827-557766562222",
    "comment_id": "110f9500-f39c-52e5-b827-557766561111",
    "content": "Hi Sarah! Thanks for your interest. We're planning to launch in Europe Q2 2024. Stay tuned for updates! 🌍",
    "status": "sent",
    "sent_at": "2024-01-15T14:20:00Z",
    "created_at": "2024-01-15T14:20:00Z"
  }
}
```

## AI Integration API

### Content Generation

```http
POST /api/v1/ai/generate-content
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111
Content-Type: application/json

{
  "prompt": "Create a motivational post about productivity for LinkedIn",
  "content_type": "social_post",
  "platform": "linkedin",
  "tone": "professional",
  "length": "medium",
  "include_hashtags": true,
  "target_audience": "professionals",
  "context": {
    "industry": "technology",
    "company_voice": "innovative and approachable"
  }
}

Response 200:
{
  "success": true,
  "data": {
    "content": "🚀 Productivity isn't about doing more—it's about doing what matters most.\n\nIn our fast-paced world, it's easy to confuse being busy with being productive. True productivity comes from:\n\n✅ Prioritizing high-impact tasks\n✅ Eliminating distractions\n✅ Taking strategic breaks\n✅ Focusing on outcomes, not hours\n\nWhat's your #1 productivity tip? Share below! 👇",
    "hashtags": ["#productivity", "#leadership", "#worksmarter", "#efficiency", "#professionaldevelopment"],
    "metadata": {
      "model_used": "deepseek-chat",
      "tokens_used": 156,
      "generation_time": 2.3,
      "confidence_score": 0.92
    },
    "usage": {
      "tokens_consumed": 156,
      "cost": 0.0012,
      "remaining_quota": 8844
    }
  }
}
```

### Sentiment Analysis

```http
POST /api/v1/ai/analyze-sentiment
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111
Content-Type: application/json

{
  "texts": [
    "Love this product! Amazing quality and fast shipping.",
    "The customer service was terrible. Very disappointed.",
    "It's okay, nothing special but does the job."
  ]
}

Response 200:
{
  "success": true,
  "data": {
    "results": [
      {
        "text": "Love this product! Amazing quality and fast shipping.",
        "sentiment": "positive",
        "confidence": 0.95,
        "scores": {
          "positive": 0.95,
          "negative": 0.02,
          "neutral": 0.03
        },
        "emotions": ["joy", "satisfaction"]
      },
      {
        "text": "The customer service was terrible. Very disappointed.",
        "sentiment": "negative",
        "confidence": 0.89,
        "scores": {
          "positive": 0.05,
          "negative": 0.89,
          "neutral": 0.06
        },
        "emotions": ["anger", "disappointment"]
      },
      {
        "text": "It's okay, nothing special but does the job.",
        "sentiment": "neutral",
        "confidence": 0.78,
        "scores": {
          "positive": 0.15,
          "negative": 0.07,
          "neutral": 0.78
        },
        "emotions": ["indifference"]
      }
    ],
    "summary": {
      "overall_sentiment": "mixed",
      "positive_count": 1,
      "negative_count": 1,
      "neutral_count": 1
    },
    "usage": {
      "tokens_consumed": 89,
      "cost": 0.0007,
      "remaining_quota": 8755
    }
  }
}
```

### Content Optimization

```http
POST /api/v1/ai/optimize-content
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111
Content-Type: application/json

{
  "content": "Check out our new product. It's really good and you should buy it.",
  "platform": "instagram",
  "optimization_goals": ["engagement", "reach", "conversions"],
  "target_audience": "millennials",
  "brand_voice": "friendly and authentic"
}

Response 200:
{
  "success": true,
  "data": {
    "optimized_content": "🌟 Just dropped: Our game-changing new product that's about to revolutionize your daily routine! \n\nWhy you'll love it:\n✨ Saves you 2+ hours daily\n✨ Eco-friendly & sustainable\n✨ Loved by 10k+ happy customers\n\nReady to upgrade your life? Link in bio! 👆\n\nWhat's your biggest daily challenge? Tell us below! 👇",
    "improvements": [
      {
        "type": "engagement",
        "description": "Added emojis and call-to-action questions",
        "impact": "Expected 35% increase in comments"
      },
      {
        "type": "structure",
        "description": "Improved formatting with bullet points",
        "impact": "Better readability and scanning"
      },
      {
        "type": "social_proof",
        "description": "Added customer testimonial reference",
        "impact": "Increased trust and credibility"
      }
    ],
    "suggested_hashtags": ["#gamechanging", "#productivity", "#sustainable", "#lifestyle", "#innovation"],
    "best_posting_time": "2024-01-16T19:00:00Z",
    "usage": {
      "tokens_consumed": 234,
      "cost": 0.0018,
      "remaining_quota": 8521
    }
  }
}
```

## Analytics API

### Performance Metrics

```http
GET /api/v1/analytics/performance
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111

Query Parameters:
- start_date: 2024-01-01
- end_date: 2024-01-15
- platforms: facebook,instagram,linkedin
- metrics: engagement,reach,impressions,clicks
- granularity: day|week|month

Response 200:
{
  "success": true,
  "data": {
    "summary": {
      "total_posts": 45,
      "total_engagement": 2847,
      "total_reach": 15420,
      "total_impressions": 28950,
      "engagement_rate": 0.098,
      "growth_rate": 0.15
    },
    "platform_breakdown": {
      "facebook": {
        "posts": 18,
        "engagement": 1245,
        "reach": 6780,
        "impressions": 12450
      },
      "instagram": {
        "posts": 15,
        "engagement": 892,
        "reach": 4920,
        "impressions": 8750
      },
      "linkedin": {
        "posts": 12,
        "engagement": 710,
        "reach": 3720,
        "impressions": 7750
      }
    },
    "time_series": [
      {
        "date": "2024-01-01",
        "engagement": 156,
        "reach": 890,
        "impressions": 1650
      },
      {
        "date": "2024-01-02",
        "engagement": 203,
        "reach": 1120,
        "impressions": 2100
      }
    ],
    "top_performing_posts": [
      {
        "id": "cc0f9500-f39c-52e5-b827-557766557777",
        "title": "New Product Launch",
        "engagement": 245,
        "reach": 1850,
        "engagement_rate": 0.132
      }
    ]
  }
}
```

### AI Usage Analytics

```http
GET /api/v1/analytics/ai-usage
Authorization: Bearer {access_token}
X-Team-ID: 660f9500-f39c-52e5-b827-557766551111

Query Parameters:
- start_date: 2024-01-01
- end_date: 2024-01-15
- feature_type: content_generation|sentiment_analysis|optimization

Response 200:
{
  "success": true,
  "data": {
    "summary": {
      "total_requests": 156,
      "total_tokens": 45230,
      "total_cost": 12.45,
      "average_response_time": 2.8,
      "success_rate": 0.987
    },
    "feature_breakdown": {
      "content_generation": {
        "requests": 89,
        "tokens": 28450,
        "cost": 8.20,
        "avg_response_time": 3.2
      },
      "sentiment_analysis": {
        "requests": 45,
        "tokens": 12340,
        "cost": 2.85,
        "avg_response_time": 1.8
      },
      "optimization": {
        "requests": 22,
        "tokens": 4440,
        "cost": 1.40,
        "avg_response_time": 4.1
      }
    },
    "usage_trends": [
      {
        "date": "2024-01-01",
        "requests": 8,
        "tokens": 2340,
        "cost": 0.65
      }
    ],
    "quota_status": {
      "current_usage": 45230,
      "monthly_limit": 100000,
      "remaining": 54770,
      "reset_date": "2024-02-01T00:00:00Z"
    }
  }
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid",
    "details": {
      "field_errors": {
        "email": ["This field is required"],
        "password": ["Password must be at least 8 characters"]
      }
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

### HTTP Status Codes

```
200 OK - Request successful
201 Created - Resource created successfully
400 Bad Request - Invalid request data
401 Unauthorized - Authentication required
403 Forbidden - Insufficient permissions
404 Not Found - Resource not found
409 Conflict - Resource already exists
422 Unprocessable Entity - Validation errors
429 Too Many Requests - Rate limit exceeded
500 Internal Server Error - Server error
503 Service Unavailable - Service temporarily unavailable
```

### Error Codes

```
AUTH_001 - Invalid credentials
AUTH_002 - Token expired
AUTH_003 - Insufficient permissions
VALID_001 - Required field missing
VALID_002 - Invalid field format
VALID_003 - Field value out of range
RESRC_001 - Resource not found
RESRC_002 - Resource already exists
RESRC_003 - Resource conflict
RATE_001 - Rate limit exceeded
RATE_002 - Quota exceeded
AI_001 - AI service unavailable
AI_002 - Invalid AI request
SOCIAL_001 - Platform connection failed
SOCIAL_002 - Platform API error
```

## Rate Limiting

### Rate Limit Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 3600
```

### Rate Limit Tiers

```
Free Plan:
- 100 requests/hour
- 1,000 requests/day

Starter Plan:
- 500 requests/hour
- 10,000 requests/day

Professional Plan:
- 2,000 requests/hour
- 50,000 requests/day

Business Plan:
- 5,000 requests/hour
- 100,000 requests/day

Enterprise Plan:
- Custom limits
```

## API Versioning

### Version Strategy

```
Current Version: v1
URL Format: /api/v1/endpoint
Header Format: Accept: application/vnd.clientnest.v1+json

Version Lifecycle:
- v1: Current (Stable)
- v2: Development (Beta)
- v0: Deprecated (6 months notice)
```

### Backward Compatibility

```json
{
  "api_version": "1.0",
  "supported_versions": ["1.0", "1.1"],
  "deprecated_versions": ["0.9"],
  "deprecation_notice": {
    "version": "0.9",
    "sunset_date": "2024-06-01T00:00:00Z",
    "migration_guide": "https://docs.clientnest.com/migration/v0-to-v1"
  }
}
```

---

*This API design provides a comprehensive foundation for ClientNest's backend services, ensuring scalability, security, and developer-friendly integration.*