# Microservices Communication Architecture

This document outlines the communication patterns, protocols, and data flow between microservices in the ClientNest AI-powered social media management platform.

## Service Architecture Overview

### Core Business Services

#### User Service
- **Port**: 8001
- **Responsibilities**: User management, authentication, profiles
- **Database**: PostgreSQL (users, profiles, permissions)
- **Team Ownership**: Backend Team (Mukiisa Mark, Atim Carol)
- **Key Endpoints**:
  - `POST /api/users/register` - User registration
  - `POST /api/users/login` - User authentication
  - `GET /api/users/profile` - User profile retrieval
  - `PUT /api/users/profile` - Profile updates
  - `GET /api/users/{id}` - Get user by ID
  - `DELETE /api/users/{id}` - Delete user account

#### Content Service
- **Port**: 8002
- **Responsibilities**: Content management, posts, analytics
- **Database**: PostgreSQL (posts, content metadata, analytics)
- **Team Ownership**: Backend Team (Mukiisa Mark, Atim Carol)
- **Key Endpoints**:
  - `POST /api/content/posts` - Create new post
  - `GET /api/content/posts` - List posts with filters
  - `PUT /api/content/posts/{id}` - Update post
  - `DELETE /api/content/posts/{id}` - Delete post
  - `GET /api/content/analytics` - Content performance analytics

#### Social Service
- **Port**: 8003
- **Responsibilities**: Platform integrations, account management
- **Database**: PostgreSQL (social accounts, platform configs)
- **Team Ownership**: Backend Team + AI Team (collaborative)
- **Key Endpoints**:
  - `POST /api/social/connect` - Connect social media account
  - `GET /api/social/accounts` - List connected accounts
  - `POST /api/social/publish` - Publish content to platforms
  - `GET /api/social/metrics` - Retrieve platform metrics
  - `GET /api/social/platforms` - List supported platforms

#### Analytics Service
- **Port**: 8004
- **Responsibilities**: Social media insights, performance metrics, reporting
- **Database**: PostgreSQL + TimescaleDB (time-series analytics data)
- **Team Ownership**: Data Science Team (Yolamu Timothy, Apunyo Mark, Nabukera Remmy)
- **Key Endpoints**:
  - `GET /api/analytics/dashboard` - Dashboard metrics
  - `GET /api/analytics/posts/{id}/performance` - Post performance data
  - `GET /api/analytics/audience` - Audience insights
  - `GET /api/analytics/trends` - Trending topics and hashtags
  - `POST /api/analytics/reports` - Generate custom reports

#### AI Service
- **Port**: 8005
- **Responsibilities**: Content generation, sentiment analysis, AI models
- **Database**: PostgreSQL (AI model configs, generated content cache)
- **Team Ownership**: AI Team (Onyait Elias, Buwembo Denzel, Biyo Stella)
- **Key Endpoints**:
  - `POST /api/ai/generate/content` - Generate social media content
  - `POST /api/ai/analyze/sentiment` - Analyze content sentiment
  - `POST /api/ai/optimize/hashtags` - Suggest optimal hashtags
  - `POST /api/ai/schedule/optimal` - Suggest optimal posting times
  - `GET /api/ai/models/status` - AI model health status

### Infrastructure Services

#### API Gateway
- **Port**: 8000
- **Responsibilities**: Request routing, load balancing, authentication
- **Team Ownership**: Backend Team (Mukiisa Mark, Atim Carol)
- **Key Features**:
  - Service discovery and routing
  - JWT authentication validation
  - Rate limiting and throttling
  - Request/response logging
  - Health check aggregation

#### Notification Service
- **Port**: 8006
- **Responsibilities**: Real-time notifications, alerts, email/SMS
- **Database**: PostgreSQL (notification templates, delivery logs)
- **Team Ownership**: Frontend Team + Backend Team (collaborative)
- **Key Endpoints**:
  - `POST /api/notifications/send` - Send notification
  - `GET /api/notifications/user/{id}` - Get user notifications
  - `PUT /api/notifications/{id}/read` - Mark as read
  - `POST /api/notifications/subscribe` - Subscribe to topics

#### Queue Service
- **Port**: 8007
- **Responsibilities**: Message queuing, async processing, job scheduling
- **Technology**: Redis + Celery
- **Team Ownership**: Backend Team + Cloud Team (collaborative)
- **Key Features**:
  - Task queue management
  - Scheduled job processing
  - Dead letter queue handling
  - Queue monitoring and metrics

#### Security Service
- **Port**: 8008
- **Responsibilities**: Authentication, authorization, security monitoring
- **Database**: PostgreSQL (security logs, access tokens)
- **Team Ownership**: Security Team (Twinamastiko Brinton, Odoi Imma, Stuart)
- **Key Endpoints**:
  - `POST /api/security/validate` - Validate access tokens
  - `POST /api/security/audit` - Log security events
  - `GET /api/security/threats` - Threat detection alerts
  - `POST /api/security/permissions` - Check user permissions

#### File Service
- **Port**: 8009
- **Responsibilities**: File upload, storage, media processing
- **Storage**: AWS S3 / Local storage
- **Team Ownership**: Backend Team + Cloud Team (collaborative)
- **Key Endpoints**:
  - `POST /api/files/upload` - Upload media files
  - `GET /api/files/{id}` - Retrieve file metadata
  - `DELETE /api/files/{id}` - Delete file
  - `POST /api/files/process` - Process media (resize, optimize)

#### Webhook Service
- **Port**: 8010
- **Responsibilities**: External integrations, event processing
- **Database**: PostgreSQL (webhook configs, delivery logs)
- **Team Ownership**: Backend Team + Security Team (collaborative)
- **Key Endpoints**:
  - `POST /api/webhooks/register` - Register webhook endpoint
  - `POST /api/webhooks/trigger` - Trigger webhook events
  - `GET /api/webhooks/logs` - Webhook delivery logs
  - `PUT /api/webhooks/{id}/retry` - Retry failed webhooks

## Communication Patterns

### 1. Synchronous Communication (REST APIs)

**Primary Pattern**: Direct HTTP/HTTPS requests between services via API Gateway

**Use Cases**:
- User authentication and authorization
- Real-time data retrieval
- Immediate response requirements
- Service health checks

**Example Flow - Content Publishing**:
```
Frontend → API Gateway → User Service (auth) → Content Service → Social Service → External APIs
```

**Implementation**:
- RESTful API design with OpenAPI documentation
- JWT token validation at API Gateway
- Request/response logging and monitoring
- Circuit breaker pattern for resilience
- Rate limiting and throttling

Direct service-to-service communication for immediate responses.

**Key Routes**:
- `Frontend → API Gateway → User Service` (Authentication)
- `Frontend → API Gateway → Content Service` (Content Management)
- `Frontend → API Gateway → Social Service` (Platform Integration)
- `Frontend → API Gateway → Analytics Service` (Real-time Metrics)

**Authentication Flow**:
```
1. User login request → API Gateway
2. API Gateway → User Service (validate credentials)
3. User Service → Security Service (generate JWT)
4. JWT returned through API Gateway → Frontend
5. Subsequent requests include JWT in headers
```

#### User Service Communications
```
User Service ←→ Security Service
├── POST /auth/validate-token
├── GET /auth/user-permissions
└── POST /auth/refresh-token

User Service ←→ File Service
├── POST /files/profile-upload
├── GET /files/user-media
└── DELETE /files/cleanup-user

User Service ←→ Analytics Service
├── POST /analytics/user-event
├── GET /analytics/user-stats
└── POST /analytics/track-login
```

#### Content Service Communications
```
Content Service ←→ File Service
├── POST /files/media-upload
├── GET /files/media-metadata
├── POST /files/process-video
└── DELETE /files/remove-media

Content Service ←→ AI Service
├── POST /ai/generate-content
├── POST /ai/optimize-hashtags
├── POST /ai/analyze-sentiment
└── GET /ai/content-suggestions

Content Service ←→ Social Media Service
├── POST /social/publish-content
├── GET /social/platform-limits
└── POST /social/schedule-post
```

#### Analytics Service Communications
```
Analytics Service ←→ All Services
├── POST /analytics/track-event
├── POST /analytics/performance-metric
├── GET /analytics/service-health
└── POST /analytics/error-log
```

### 2. Asynchronous Communication (Message Queues)

Event-driven communication through Redis queues for non-blocking operations.

#### Queue Service Coordination
```
Queue Service manages:
├── content_publishing_queue
│   ├── schedule_post_job
│   ├── bulk_publish_job
│   └── cross_platform_sync_job
├── analytics_processing_queue
│   ├── engagement_calculation_job
│   ├── report_generation_job
│   └── data_aggregation_job
├── notification_delivery_queue
│   ├── email_notification_job
│   ├── push_notification_job
│   └── sms_notification_job
├── file_processing_queue
│   ├── image_optimization_job
│   ├── video_transcoding_job
│   └── thumbnail_generation_job
└── webhook_processing_queue
    ├── external_event_job
    ├── integration_sync_job
    └── callback_processing_job
```

#### Message Queue Examples

**Content Publishing Flow:**
```python
# Content Service publishes to queue
queue_service.publish('content_publishing_queue', {
    'job_type': 'schedule_post',
    'content_id': 'content_123',
    'platforms': ['facebook', 'twitter', 'linkedin'],
    'scheduled_time': '2024-01-15T10:00:00Z',
    'user_id': 'user_456'
})

# Social Media Service processes the job
def process_scheduled_post(job_data):
    content = content_service.get_content(job_data['content_id'])
    for platform in job_data['platforms']:
        platform_service = get_platform_service(platform)
        result = platform_service.publish(content)
        analytics_service.track_publish_event(result)
```

**Analytics Processing Flow:**
```python
# Multiple services send analytics events
queue_service.publish('analytics_processing_queue', {
    'event_type': 'content_engagement',
    'content_id': 'content_123',
    'platform': 'facebook',
    'engagement_data': {
        'likes': 45,
        'shares': 12,
        'comments': 8
    },
    'timestamp': '2024-01-15T10:30:00Z'
})

# Analytics Service processes engagement data
def process_engagement_event(event_data):
    engagement_calculator.update_metrics(event_data)
    if engagement_calculator.is_viral_threshold_reached(event_data):
        notification_service.send_viral_alert(event_data)
```

### 3. Event-Driven Communication (Webhooks)

**Primary Pattern**: External integrations and real-time event processing

**Webhook Service Responsibilities**:
- Receive external webhook events
- Validate and authenticate incoming requests
- Route events to appropriate services
- Retry failed deliveries with exponential backoff
- Log all webhook activities for audit
- Handle webhook security and verification

**External Integration Examples**:

**Social Media Platform Events**:
```
Facebook/Instagram → Webhook Service → Social Service → Analytics Service → Notification Service
```

**Third-party Tool Integrations**:
```
Zapier/IFTTT → Webhook Service → Content Service → Queue Service → AI Service
```

**Payment/Subscription Events**:
```
Stripe/PayPal → Webhook Service → User Service → Security Service → Notification Service
```

**GitHub Integration (for development)**:
```
GitHub → Webhook Service → Security Service → Notification Service
```

**Webhook Configuration**:
- **Retry Policy**: 3 attempts with exponential backoff
- **Timeout**: 30 seconds per request
- **Max Payload**: 10MB
- **Security**: HMAC signature verification
- **Rate Limiting**: 1000 requests per minute per endpoint

Real-time event propagation for external integrations and system events.

#### Webhook Service Event Handling
```
Webhook Service processes:
├── External Platform Events
│   ├── facebook_page_mention
│   ├── twitter_direct_message
│   ├── instagram_comment
│   └── linkedin_connection_request
├── Payment Processing Events
│   ├── subscription_created
│   ├── payment_successful
│   ├── payment_failed
│   └── subscription_cancelled
├── Third-Party Integration Events
│   ├── zapier_trigger
│   ├── ifttt_action
│   ├── slack_command
│   └── discord_webhook
└── Internal System Events
    ├── user_registration
    ├── content_published
    ├── analytics_threshold_reached
    └── security_alert
```

#### Webhook Processing Example
```python
# Webhook Service receives external event
@webhook_handler('/webhooks/facebook')
def handle_facebook_webhook(request):
    event_data = validate_facebook_signature(request)
    
    if event_data['type'] == 'page_mention':
        # Process mention event
        queue_service.publish('notification_delivery_queue', {
            'type': 'social_mention',
            'platform': 'facebook',
            'user_id': get_user_by_page_id(event_data['page_id']),
            'mention_data': event_data['data']
        })
        
        # Track analytics
        analytics_service.track_mention_event(event_data)
    
    return {'status': 'processed'}
```

## 🔐 Security & Authentication Flow

### Security Architecture

**Authentication & Authorization**:
- **JWT-Based Authentication**: Stateless token-based authentication managed by Security Service
- **Token validation**: Performed at API Gateway level for all requests
- **Service-to-service authentication**: Internal tokens with service-specific scopes
- **Automatic token refresh**: Seamless token renewal mechanism
- **Token blacklisting**: Immediate revocation for logout/security events

**Role-Based Access Control (RBAC)**:
- **User roles**: Admin, Manager, Editor, Viewer, Developer
- **Service-level permissions**: Granular access control per microservice
- **Resource-based access**: Fine-grained permissions per resource type
- **Dynamic permission evaluation**: Real-time permission checks through Security Service
- **Team-based access**: Collaborative access control for team features

### Security Monitoring

**Security Service Responsibilities** (Security Team: Twinamastiko Brinton, Odoi Imma, Stuart):
- Real-time threat detection and automated alerting
- Comprehensive audit logging and compliance reporting
- Access pattern analysis and anomaly detection
- Automated vulnerability scanning and assessment
- Security incident response and remediation workflows
- API security monitoring and intelligent rate limiting

**Security Events Tracked**:
- Failed authentication attempts and brute force detection
- Unusual access patterns and geographic anomalies
- API rate limit violations and abuse detection
- Suspicious file uploads and malware scanning
- External integration security events
- Cross-service communication security violations
- Data access and modification audit trails

**Security Integration Points**:
- **API Gateway**: Authentication, rate limiting, request validation
- **User Service**: Identity management, password policies
- **File Service**: Malware scanning, content validation
- **Webhook Service**: Signature verification, payload validation
- **All Services**: Audit logging, security event reporting

### Service-to-Service Authentication
```
1. Service Request → API Gateway
2. API Gateway → Security Service (validate service token)
3. Security Service → User Service (validate user permissions)
4. Security Service → Target Service (authorized request with context)
5. Target Service → Security Service (audit log)
6. Target Service → Response to client
```

### Authentication Token Flow
```python
# Service-to-service authentication
class ServiceAuthenticator:
    def __init__(self, service_name, secret_key):
        self.service_name = service_name
        self.secret_key = secret_key
    
    def get_service_token(self):
        payload = {
            'service': self.service_name,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'scopes': self.get_service_scopes()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def make_authenticated_request(self, target_service, endpoint, data):
        headers = {
            'Authorization': f'Bearer {self.get_service_token()}',
            'X-Service-Name': self.service_name,
            'X-Correlation-ID': self.get_correlation_id()
        }
        return requests.post(f'{target_service}{endpoint}', 
                           json=data, headers=headers)
    
    def get_service_scopes(self):
        # Define service-specific permissions
        service_scopes = {
            'user-service': ['user:read', 'user:write', 'auth:validate'],
            'content-service': ['content:read', 'content:write', 'media:process'],
            'analytics-service': ['analytics:read', 'metrics:write', 'reports:generate']
        }
        return service_scopes.get(self.service_name, [])
```

## 📊 Data Flow Patterns

### Real-time Data Flow
```
User Action → Service → Queue Service → Processing Service → Analytics Service
                ↓
         Notification Service → User (real-time alert)
                ↓
         Webhook Service → External Systems
```

### Batch Processing Flow
```
Scheduled Jobs → Queue Service → Batch Processor → File Service (reports)
                                        ↓
                              Analytics Service (aggregation)
                                        ↓
                              Notification Service (summary alerts)
```

### Content Publishing Flow
```
Content Creation → Content Service → AI Service (optimization)
                                          ↓
                   File Service ← Media Processing
                                          ↓
                   Queue Service → Social Media Service → External Platforms
                                          ↓
                   Analytics Service ← Engagement Tracking
```

## 🚨 Error Handling & Resilience

### Circuit Breaker Pattern
```python
class ServiceCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call_service(self, service_func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise ServiceUnavailableError("Circuit breaker is OPEN")
        
        try:
            result = service_func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise e
```

### Retry Mechanism
```python
class RetryHandler:
    @staticmethod
    def exponential_backoff_retry(func, max_retries=3, base_delay=1):
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                logger.warning(f"Retry attempt {attempt + 1} after {delay}s delay")
```

## 📈 Monitoring & Observability

### Health Checks

**Service Health Endpoints** (implemented by all services):
- `GET /health` - Basic service status and uptime
- `GET /health/detailed` - Comprehensive health with dependencies
- `GET /metrics` - Prometheus-compatible metrics export
- `GET /health/ready` - Readiness probe for Kubernetes
- `GET /health/live` - Liveness probe for container orchestration

**Health Check Components**:
- Database connectivity and query performance
- External API availability and response times
- Queue service status and message processing
- Memory and CPU usage thresholds
- Disk space availability and I/O performance
- Service dependencies and circuit breaker status

### Logging Strategy

**Centralized Logging** (Cloud Team responsibility: Edwin):
- **Technology Stack**: ELK Stack (Elasticsearch, Logstash, Kibana) or EFK (Fluentd)
- **Log Levels**: DEBUG, INFO, WARN, ERROR, FATAL
- **Structured Logging**: JSON format with correlation IDs and service metadata
- **Log Retention**: 30 days for application logs, 90 days for security logs

**Log Categories by Service**:
- **Application Logs**: Business logic events, user actions, service interactions
- **Access Logs**: API request/response details, authentication events
- **Error Logs**: Exception tracking, stack traces, error context
- **Security Logs**: Authentication, authorization, security events (Security Team)
- **Performance Logs**: Response times, resource usage, bottleneck analysis
- **Audit Logs**: Data access, modifications, compliance events

### Metrics & Alerting

**Key Metrics by Service Type**:

**API Gateway Metrics**:
- Request rate and distribution across services
- Response times (p50, p95, p99)
- Error rates by service and endpoint
- Authentication success/failure rates
- Rate limiting triggers

**Business Service Metrics**:
- Service-specific business metrics (posts created, users registered)
- Database query performance and connection pool usage
- External API call success rates and latencies
- Cache hit/miss ratios

**Infrastructure Metrics**:
- Resource utilization (CPU, Memory, Disk, Network)
- Queue processing times and backlog sizes
- Database performance and replication lag
- File storage usage and transfer rates

**Alerting Rules** (managed by Cloud Team with Security Team input):
- **Critical**: Service downtime (> 30 seconds), High error rates (> 5%)
- **Warning**: Slow response times (> 2 seconds), Queue backlog (> 1000 messages)
- **Info**: Resource usage (> 80%), Unusual traffic patterns
- **Security**: Failed authentication spikes, Suspicious access patterns

**Alert Channels**:
- **Slack**: Real-time notifications for development teams
- **Email**: Critical alerts and daily summaries
- **PagerDuty**: On-call escalation for production issues
- **Dashboard**: Visual monitoring for all stakeholders

### Service Health Checks

**Implementation Example**:
```python
# Health check endpoint for each service
@app.route('/health')
def health_check():
    health_status = {
        'service': SERVICE_NAME,
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': {},
        'uptime': get_service_uptime()
    }
    
    # Check database connection
    try:
        db.session.execute('SELECT 1')
        health_status['dependencies']['database'] = 'healthy'
    except Exception:
        health_status['dependencies']['database'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    # Check Redis connection
    try:
        redis_client.ping()
        health_status['dependencies']['redis'] = 'healthy'
    except Exception:
        health_status['dependencies']['redis'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    return jsonify(health_status)
```

### Distributed Tracing

**Implementation** (Cloud Team responsibility: Edwin):
- **Technology**: Jaeger or Zipkin with OpenTelemetry
- **Trace Context**: Propagated via HTTP headers across service boundaries
- **Span Creation**: Automatic for HTTP requests, manual for critical business logic
- **Sampling**: Configurable sampling rates per service (default: 10%)

**Trace Information Captured**:
- Complete request flow across all microservices
- Performance bottlenecks and latency analysis
- Error propagation paths and failure points
- Service dependency mapping and call graphs
- Database query performance and external API calls

```python
# Correlation ID for request tracing
class CorrelationMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        correlation_id = environ.get('HTTP_X_CORRELATION_ID') or str(uuid.uuid4())
        environ['correlation_id'] = correlation_id
        
        # Add to response headers
        def new_start_response(status, response_headers):
            response_headers.append(('X-Correlation-ID', correlation_id))
            return start_response(status, response_headers)
        
        return self.app(environ, new_start_response)
```

## 🔧 Configuration Management

### Service Discovery
```python
# Service registry for dynamic service discovery
class ServiceRegistry:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.services = {}
    
    def register_service(self, service_name, host, port, health_check_url):
        service_info = {
            'host': host,
            'port': port,
            'health_check_url': health_check_url,
            'registered_at': datetime.utcnow().isoformat()
        }
        self.redis.hset(f'services:{service_name}', mapping=service_info)
        self.redis.expire(f'services:{service_name}', 300)  # 5 min TTL
    
    def discover_service(self, service_name):
        service_info = self.redis.hgetall(f'services:{service_name}')
        if service_info:
            return f"http://{service_info['host']}:{service_info['port']}"
        raise ServiceNotFoundError(f"Service {service_name} not found")
```

## 📝 API Versioning Strategy

### Version Management
```python
# API versioning through headers
@app.route('/api/users', methods=['GET'])
def get_users():
    api_version = request.headers.get('API-Version', 'v1')
    
    if api_version == 'v1':
        return UserSerializerV1(users).data
    elif api_version == 'v2':
        return UserSerializerV2(users).data
    else:
        return {'error': 'Unsupported API version'}, 400
```

## 🚀 Deployment Considerations

### Service Deployment Order
1. **Infrastructure Services**: Security, Queue, File, Webhook
2. **Core Services**: User, Content, Social Media
3. **Analytics Services**: Analytics, Notification
4. **API Gateway**: Route configuration and load balancing

### Rolling Deployment Strategy
```yaml
# Kubernetes deployment with rolling updates
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      containers:
      - name: user-service
        image: clientnest/user-service:latest
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

This communication guide ensures all team members understand how services interact, enabling efficient development and maintenance of the ClientNest microservices architecture.