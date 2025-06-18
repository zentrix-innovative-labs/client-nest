# ClientNest Database Design

## Database Architecture Overview

ClientNest uses a **multi-database architecture** to optimize performance, scalability, and cost:

- **PostgreSQL**: Primary transactional database
- **Redis**: Caching and session storage
- **TimescaleDB**: Time-series data for analytics
- **AWS S3**: File and media storage

## Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              POSTGRESQL SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Users      │    │      Teams      │    │   TeamMembers   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ email           │    │ name            │    │ user_id (FK)    │
│ password_hash   │    │ owner_id (FK)   │────│ team_id (FK)    │
│ first_name      │    │ plan_type       │    │ role            │
│ last_name       │    │ created_at      │    │ joined_at       │
│ avatar_url      │    │ updated_at      │    │ permissions     │
│ timezone        │    │ settings        │    │ status          │
│ is_active       │    │ billing_info    │    └─────────────────┘
│ email_verified  │    └─────────────────┘           │
│ created_at      │           │                      │
│ updated_at      │           │                      │
│ last_login      │           │                      │
│ preferences     │           │                      │
└─────────────────┘           │                      │
        │                     │                      │
        └─────────────────────┼──────────────────────┘
                              │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ SocialAccounts  │    │     Posts       │    │   PostMedia     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ user_id (FK)    │────│ user_id (FK)    │    │ post_id (FK)    │
│ team_id (FK)    │    │ team_id (FK)    │    │ media_type      │
│ platform        │    │ title           │    │ file_url        │
│ platform_id     │    │ content         │    │ file_size       │
│ username        │    │ hashtags        │    │ dimensions      │
│ access_token    │    │ status          │    │ alt_text        │
│ refresh_token   │    │ scheduled_at    │    │ order_index     │
│ token_expires   │    │ published_at    │    │ created_at      │
│ permissions     │    │ ai_generated    │    └─────────────────┘
│ is_active       │    │ ai_prompt       │           │
│ created_at      │    │ engagement      │           │
│ updated_at      │    │ created_at      │           │
└─────────────────┘    │ updated_at      │           │
        │              │ metadata        │           │
        │              └─────────────────┘           │
        │                      │                     │
        │                      └─────────────────────┘
        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Comments      │    │   Responses     │    │   Templates     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ account_id (FK) │────│ comment_id (FK) │    │ user_id (FK)    │
│ platform_id     │    │ user_id (FK)    │    │ team_id (FK)    │
│ content         │    │ content         │    │ name            │
│ author_name     │    │ ai_generated    │    │ description     │
│ author_id       │    │ sent_at         │    │ content         │
│ sentiment       │    │ status          │    │ category        │
│ priority        │    │ created_at      │    │ hashtags        │
│ status          │    └─────────────────┘    │ is_public       │
│ replied_at      │           │               │ usage_count     │
│ created_at      │           │               │ created_at      │
│ metadata        │           │               │ updated_at      │
└─────────────────┘           │               └─────────────────┘
        │                     │                      │
        └─────────────────────┘                      │
                                                     │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Schedules     │    │   Automations   │    │   Webhooks      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ user_id (FK)    │    │ user_id (FK)    │    │ user_id (FK)    │
│ team_id (FK)    │    │ team_id (FK)    │    │ platform        │
│ post_id (FK)    │    │ name            │    │ event_type      │
│ platform        │    │ description     │    │ endpoint_url    │
│ scheduled_time  │    │ trigger_type    │    │ secret_key      │
│ timezone        │    │ trigger_config  │    │ is_active       │
│ status          │    │ action_type     │    │ last_triggered  │
│ retry_count     │    │ action_config   │    │ created_at      │
│ last_attempt    │    │ is_active       │    │ updated_at      │
│ created_at      │    │ created_at      │    └─────────────────┘
│ updated_at      │    │ updated_at      │
└─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AIUsage       │    │   Billing       │    │   Notifications │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ user_id (FK)    │    │ team_id (FK)    │    │ user_id (FK)    │
│ team_id (FK)    │    │ subscription_id │    │ type            │
│ feature_type    │    │ plan_type       │    │ title           │
│ tokens_used     │    │ amount          │    │ message         │
│ cost            │    │ currency        │    │ data            │
│ model_used      │    │ status          │    │ is_read         │
│ request_data    │    │ period_start    │    │ priority        │
│ response_data   │    │ period_end      │    │ created_at      │
│ created_at      │    │ created_at      │    │ read_at         │
│ metadata        │    │ updated_at      │    └─────────────────┘
└─────────────────┘    │ next_billing    │
                       └─────────────────┘
```

## Redis Cache Schema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                REDIS SCHEMA                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

Key Patterns:

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sessions      │    │   User Cache    │    │  API Cache      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ session:{id}    │    │ user:{id}       │    │ api:{endpoint}  │
│ - user_id       │    │ - profile_data  │    │ - response_data │
│ - expires_at    │    │ - preferences   │    │ - expires_at    │
│ - permissions   │    │ - team_data     │    │ - cache_key     │
│ - last_activity │    │ - settings      │    └─────────────────┘
└─────────────────┘    │ - expires_at    │
                       └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Queue Jobs     │    │  Rate Limits    │    │  Temp Data      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ queue:{name}    │    │ rate:{user_id}  │    │ temp:{key}      │
│ - job_data      │    │ - request_count │    │ - data          │
│ - priority      │    │ - window_start  │    │ - expires_at    │
│ - retry_count   │    │ - expires_at    │    └─────────────────┘
│ - created_at    │    └─────────────────┘
└─────────────────┘
```

## TimescaleDB Analytics Schema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            TIMESCALEDB SCHEMA                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Events        │    │   Metrics       │    │   Performance   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ time (PK)       │    │ time (PK)       │    │ time (PK)       │
│ user_id         │    │ user_id         │    │ service_name    │
│ team_id         │    │ team_id         │    │ endpoint        │
│ event_type      │    │ metric_name     │    │ response_time   │
│ event_data      │    │ metric_value    │    │ status_code     │
│ platform        │    │ dimensions      │    │ error_count     │
│ session_id      │    │ tags            │    │ memory_usage    │
│ ip_address      │    └─────────────────┘    │ cpu_usage       │
│ user_agent      │                           └─────────────────┘
└─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Engagement     │    │   AI_Metrics    │    │   Costs         │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ time (PK)       │    │ time (PK)       │    │ time (PK)       │
│ post_id         │    │ user_id         │    │ user_id         │
│ platform        │    │ team_id         │    │ team_id         │
│ likes           │    │ feature_type    │    │ service_type    │
│ comments        │    │ tokens_used     │    │ cost_amount     │
│ shares          │    │ model_used      │    │ currency        │
│ views           │    │ response_time   │    │ billing_period  │
│ reach           │    │ success_rate    │    └─────────────────┘
│ impressions     │    └─────────────────┘
└─────────────────┘
```

## Data Models (Django Models)

### User Management Models

```python
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar_url = models.URLField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    preferences = models.JSONField(default=dict)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    plan_type = models.CharField(max_length=20, choices=[
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    settings = models.JSONField(default=dict)
    billing_info = models.JSONField(default=dict)

class TeamMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer')
    ])
    joined_at = models.DateTimeField(auto_now_add=True)
    permissions = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default='active')
    
    class Meta:
        unique_together = ['user', 'team']
```

### Social Media Models

```python
# social/models.py
from django.db import models
from users.models import User, Team
import uuid

class SocialAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('pinterest', 'Pinterest')
    ])
    platform_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expires = models.DateTimeField(null=True, blank=True)
    permissions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['platform', 'platform_id', 'team']

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    hashtags = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed')
    ], default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    engagement = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)

class PostMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=20, choices=[
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF')
    ])
    file_url = models.URLField()
    file_size = models.BigIntegerField()
    dimensions = models.JSONField(default=dict)  # {"width": 1080, "height": 1080}
    alt_text = models.TextField(blank=True)
    order_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

### AI and Content Models

```python
# ai/models.py
from django.db import models
from users.models import User, Team
from social.models import SocialAccount
import uuid

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    platform_id = models.CharField(max_length=100)  # Platform's comment ID
    content = models.TextField()
    author_name = models.CharField(max_length=100)
    author_id = models.CharField(max_length=100)
    sentiment = models.CharField(max_length=20, choices=[
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral')
    ], null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('replied', 'Replied'),
        ('ignored', 'Ignored'),
        ('flagged', 'Flagged')
    ], default='new')
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

class Response(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    ai_generated = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

class Template(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    content = models.TextField()
    category = models.CharField(max_length=50)
    hashtags = models.JSONField(default=list)
    is_public = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AIUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    feature_type = models.CharField(max_length=50, choices=[
        ('content_generation', 'Content Generation'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('response_generation', 'Response Generation'),
        ('content_optimization', 'Content Optimization')
    ])
    tokens_used = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=4)
    model_used = models.CharField(max_length=50)
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
```

### Automation and Scheduling Models

```python
# automation/models.py
from django.db import models
from users.models import User, Team
from social.models import Post
import uuid

class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20)
    scheduled_time = models.DateTimeField()
    timezone = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    retry_count = models.PositiveIntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Automation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    trigger_type = models.CharField(max_length=50, choices=[
        ('comment_received', 'Comment Received'),
        ('mention_detected', 'Mention Detected'),
        ('schedule_time', 'Schedule Time'),
        ('engagement_threshold', 'Engagement Threshold')
    ])
    trigger_config = models.JSONField(default=dict)
    action_type = models.CharField(max_length=50, choices=[
        ('auto_reply', 'Auto Reply'),
        ('send_notification', 'Send Notification'),
        ('create_post', 'Create Post'),
        ('tag_user', 'Tag User')
    ])
    action_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Webhook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20)
    event_type = models.CharField(max_length=50)
    endpoint_url = models.URLField()
    secret_key = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Analytics and Billing Models

```python
# analytics/models.py
from django.db import models
from users.models import User, Team
import uuid

class Billing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=100, unique=True)
    plan_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('unpaid', 'Unpaid')
    ])
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_billing = models.DateTimeField()

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=[
        ('comment', 'New Comment'),
        ('mention', 'Mention'),
        ('post_published', 'Post Published'),
        ('post_failed', 'Post Failed'),
        ('billing', 'Billing'),
        ('system', 'System')
    ])
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
```

## Database Relationships

### Entity Relationship Diagram (ERD)

```
Users ||--o{ TeamMembers }o--|| Teams
Users ||--o{ SocialAccounts }o--|| Teams
Users ||--o{ Posts }o--|| Teams
Users ||--o{ Templates }o--|| Teams
Users ||--o{ AIUsage }o--|| Teams
Users ||--o{ Schedules }o--|| Teams
Users ||--o{ Automations }o--|| Teams
Users ||--o{ Webhooks
Users ||--o{ Responses
Users ||--o{ Notifications

Teams ||--o{ Billing

Posts ||--o{ PostMedia
Posts ||--o{ Schedules

SocialAccounts ||--o{ Comments

Comments ||--o{ Responses
```

## Database Indexes

### Primary Indexes
```sql
-- Performance-critical indexes
CREATE INDEX idx_posts_user_team ON posts(user_id, team_id);
CREATE INDEX idx_posts_status_scheduled ON posts(status, scheduled_at);
CREATE INDEX idx_comments_account_status ON comments(account_id, status);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);
CREATE INDEX idx_social_accounts_platform ON social_accounts(platform, is_active);
CREATE INDEX idx_ai_usage_team_created ON ai_usage(team_id, created_at DESC);
CREATE INDEX idx_schedules_status_time ON schedules(status, scheduled_time);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read, created_at DESC);
```

### Composite Indexes
```sql
-- Multi-column indexes for complex queries
CREATE INDEX idx_posts_team_status_created ON posts(team_id, status, created_at DESC);
CREATE INDEX idx_comments_sentiment_priority ON comments(sentiment, priority, created_at DESC);
CREATE INDEX idx_ai_usage_feature_team_date ON ai_usage(feature_type, team_id, created_at DESC);
```

## Database Constraints

### Foreign Key Constraints
```sql
-- Ensure referential integrity
ALTER TABLE team_members ADD CONSTRAINT fk_team_members_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE team_members ADD CONSTRAINT fk_team_members_team 
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE;

ALTER TABLE posts ADD CONSTRAINT fk_posts_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE posts ADD CONSTRAINT fk_posts_team 
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE;
```

### Check Constraints
```sql
-- Data validation constraints
ALTER TABLE users ADD CONSTRAINT chk_users_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE ai_usage ADD CONSTRAINT chk_ai_usage_tokens_positive 
    CHECK (tokens_used > 0);

ALTER TABLE ai_usage ADD CONSTRAINT chk_ai_usage_cost_positive 
    CHECK (cost >= 0);

ALTER TABLE schedules ADD CONSTRAINT chk_schedules_future_time 
    CHECK (scheduled_time > created_at);
```

## Data Migration Strategy

### Migration Phases

```
Phase 1: Core Tables
├── Users and Authentication
├── Teams and Memberships
└── Basic Settings

Phase 2: Social Media Integration
├── Social Accounts
├── Posts and Media
└── Platform Connections

Phase 3: AI and Automation
├── AI Usage Tracking
├── Templates and Content
├── Automation Rules
└── Scheduling System

Phase 4: Analytics and Billing
├── Analytics Tables
├── Billing Integration
├── Notifications
└── Reporting Views
```

### Sample Migration Script
```python
# migrations/0001_initial.py
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4)),
                ('email', models.EmailField(unique=True)),
                ('password_hash', models.CharField(max_length=128)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        # ... more model definitions
    ]
```

## Database Performance Optimization

### Query Optimization Strategies

```sql
-- Use EXPLAIN ANALYZE to optimize queries
EXPLAIN ANALYZE SELECT p.*, pm.file_url 
FROM posts p 
LEFT JOIN post_media pm ON p.id = pm.post_id 
WHERE p.team_id = $1 AND p.status = 'published' 
ORDER BY p.created_at DESC 
LIMIT 20;

-- Optimize with proper indexing
CREATE INDEX CONCURRENTLY idx_posts_team_status_created 
ON posts(team_id, status, created_at DESC);
```

### Connection Pooling Configuration
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'clientnest',
        'USER': 'clientnest_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        },
        'CONN_MAX_AGE': 600,  # 10 minutes
    }
}
```

## Backup and Recovery

### Backup Strategy
```bash
#!/bin/bash
# Daily backup script

# Full database backup
pg_dump -h localhost -U clientnest_user -d clientnest \
    --format=custom --compress=9 \
    --file="/backups/clientnest_$(date +%Y%m%d_%H%M%S).backup"

# Upload to S3
aws s3 cp /backups/clientnest_*.backup s3://clientnest-backups/daily/

# Clean old local backups (keep 7 days)
find /backups -name "clientnest_*.backup" -mtime +7 -delete
```

### Recovery Procedures
```bash
# Point-in-time recovery
pg_restore -h localhost -U clientnest_user -d clientnest_restored \
    --clean --if-exists --format=custom \
    /backups/clientnest_20240115_120000.backup

# Verify data integrity
psql -h localhost -U clientnest_user -d clientnest_restored \
    -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM posts;"
```

---

*This database design provides a solid foundation for ClientNest's data management needs, with proper relationships, indexing, and scalability considerations.*