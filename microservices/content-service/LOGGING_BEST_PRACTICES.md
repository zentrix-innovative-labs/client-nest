# Django Logging Best Practices Guide

## Overview
This document outlines the proper logging implementation for the ClientNest Content Service, replacing problematic `print()` statements with Django's robust logging framework.

## Why Avoid `print()` Statements in Production?

### Problems with `print()`:
1. **No Log Level Control**: Cannot filter by severity (DEBUG, INFO, WARNING, ERROR)
2. **No Formatting**: Basic string output without timestamps, modules, or structured data
3. **No File Output**: Only outputs to console, difficult to persist or analyze
4. **No Monitoring Integration**: Cannot integrate with log aggregation systems
5. **Performance Issues**: Synchronous output can block application threads
6. **No Structured Logging**: Cannot include metadata for better debugging

### Benefits of Django Logging:
1. **Log Level Management**: Control verbosity per environment
2. **Multiple Handlers**: Output to files, console, external services
3. **Structured Data**: Include contextual metadata with each log entry
4. **Performance**: Asynchronous handlers available
5. **Integration Ready**: Works with monitoring tools like ELK, Datadog, etc.

## Logging Configuration

### 1. Enhanced Settings Configuration
Located in `content_service/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'content_service.log',
            'formatter': 'verbose',
        },
        'signals_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'signals.log',
            'formatter': 'json',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'posts.signals': {
            'handlers': ['console', 'signals_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 2. Proper Signal Implementation
Before (problematic):
```python
@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    if created:
        print(f"New post created: {instance.title}")  # ❌ BAD
```

After (proper logging):
```python
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(
                "New post created",  # ✅ GOOD
                extra={
                    'post_id': instance.id,
                    'post_title': instance.title,
                    'user_id': instance.user.id if instance.user else None,
                    'team_id': instance.team.id if instance.team else None,
                    'status': instance.status,
                    'type': instance.type
                }
            )
    except Exception as e:
        logger.error(
            "Error in post_saved signal",
            extra={'error': str(e)},
            exc_info=True
        )
```

## Logging Levels and When to Use Them

### DEBUG
- Development debugging information
- Detailed execution flow
- Variable values during development

```python
logger.debug("Processing post validation", extra={'post_id': post.id})
```

### INFO
- Normal application flow
- Business logic events
- Successful operations

```python
logger.info("Post published successfully", extra={'post_id': post.id})
```

### WARNING
- Recoverable errors
- Deprecated functionality usage
- Configuration issues

```python
logger.warning("Post deleted by user", extra={'post_id': post.id})
```

### ERROR
- Application errors
- Exception handling
- Failed operations

```python
logger.error("Failed to publish post", extra={'error': str(e)}, exc_info=True)
```

### CRITICAL
- System failures
- Security breaches
- Service unavailability

```python
logger.critical("Database connection lost", exc_info=True)
```

## Structured Logging with Extra Data

### Best Practices:
1. **Include Context**: Always add relevant IDs and metadata
2. **Use Consistent Keys**: Standardize field names across logs
3. **Avoid Sensitive Data**: Never log passwords, tokens, or PII
4. **Handle Exceptions**: Always wrap in try-catch blocks

### Example Implementation:
```python
logger.info(
    "User action performed",
    extra={
        'user_id': user.id,
        'action': 'post_create',
        'resource_id': post.id,
        'resource_type': 'post',
        'timestamp': timezone.now().isoformat(),
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
    }
)
```

## Log File Organization

### File Structure:
```
logs/
├── content_service.log    # General application logs
├── signals.log           # Model signal events (JSON format)
├── errors.log            # Error-specific logs
└── access.log            # Request/response logs
```

### Log Rotation:
For production, implement log rotation:

```python
'handlers': {
    'rotating_file': {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': BASE_DIR / 'logs' / 'content_service.log',
        'maxBytes': 1024*1024*15,  # 15MB
        'backupCount': 5,
        'formatter': 'verbose',
    },
}
```

## Monitoring and Alerting

### 1. Log Aggregation
- Use ELK Stack (Elasticsearch, Logstash, Kibana)
- Integrate with cloud logging services (AWS CloudWatch, Azure Monitor)
- Set up centralized logging for microservices

### 2. Alerting Rules
- ERROR level logs → Immediate notification
- WARNING level logs → Daily summary
- High volume of logs → Performance alert

### 3. Metrics from Logs
- Post creation rates
- Error frequencies
- User activity patterns

## Performance Considerations

### 1. Asynchronous Logging
For high-traffic applications:

```python
'handlers': {
    'async_file': {
        'level': 'INFO',
        'class': 'logging.handlers.QueueHandler',
        'queue': queue.Queue(-1),
        'target': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'content_service.log',
        }
    },
}
```

### 2. Log Level Management
- Production: INFO and above
- Staging: DEBUG and above  
- Development: DEBUG and above

### 3. Conditional Logging
```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Expensive debug info: %s", expensive_operation())
```

## Security Considerations

### 1. Sensitive Data
Never log:
- Passwords
- API keys
- Personal information
- Financial data

### 2. Log Sanitization
```python
def sanitize_for_logging(data):
    """Remove sensitive information from log data"""
    sensitive_keys = ['password', 'token', 'secret', 'key']
    if isinstance(data, dict):
        return {k: '[REDACTED]' if k.lower() in sensitive_keys else v 
                for k, v in data.items()}
    return data
```

## Testing Logging

### Unit Tests
```python
import logging
from django.test import TestCase

class LoggingTestCase(TestCase):
    def setUp(self):
        self.logger = logging.getLogger('posts.signals')
        self.log_handler = logging.handlers.MemoryHandler(capacity=1000)
        self.logger.addHandler(self.log_handler)

    def test_post_creation_logging(self):
        post = Post.objects.create(title="Test Post")
        
        # Check that log was created
        self.assertEqual(len(self.log_handler.buffer), 1)
        log_record = self.log_handler.buffer[0]
        self.assertEqual(log_record.levelname, 'INFO')
        self.assertIn('New post created', log_record.getMessage())
```

## Migration Guide

### Step 1: Identify print() Statements
```bash
grep -r "print(" --include="*.py" .
```

### Step 2: Replace with Appropriate Logger
- Replace `print()` with `logger.info()`
- Add structured data with `extra` parameter
- Include error handling

### Step 3: Test Logging
- Verify logs appear in files
- Check log formatting
- Ensure proper log levels

### Step 4: Configure Production
- Set up log rotation
- Configure monitoring alerts
- Implement log shipping

## Conclusion

Proper logging is essential for:
- **Debugging**: Easier troubleshooting with structured data
- **Monitoring**: Real-time application health monitoring  
- **Compliance**: Audit trails for security and regulations
- **Performance**: Identifying bottlenecks and optimization opportunities
- **Business Intelligence**: Understanding user behavior patterns

By following these practices, the ClientNest Content Service will have robust, production-ready logging that supports debugging, monitoring, and business analytics.
