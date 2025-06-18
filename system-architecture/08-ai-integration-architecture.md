# ClientNest AI Integration Architecture

## AI Overview

ClientNest leverages **DeepSeek API** for intelligent content generation, sentiment analysis, and optimization. The AI system is designed for:

- **Cost Efficiency**: Tier-based usage limits and off-peak optimization
- **Performance**: Async processing and intelligent caching
- **Quality**: Multi-step validation and human oversight
- **Scalability**: Queue-based processing and rate limiting

## AI Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI INTEGRATION ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   API Gateway   │    │  AI Controller  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Content Editor│────│ • Rate Limiting │────│ • Request       │
│ • AI Suggestions│    │ • Usage Tracking│    │   Validation    │
│ • Progress Track│    │ • Cost Monitor  │    │ • Queue Manager │
│ • Preview Mode  │    │ • Auth Check    │    │ • Response Cache│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │                        │
                               ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            AI PROCESSING LAYER                                 │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│  Content Gen    │  Sentiment      │  Optimization   │    Queue System         │
│  Service        │  Analysis       │  Service        │                         │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Post Creation │ • Comment       │ • Content       │ • Redis Queue           │
│ • Caption Gen   │   Analysis      │   Enhancement   │ • Priority Handling     │
│ • Hashtag Suggest│ • Engagement   │ • SEO Optimize  │ • Retry Logic           │
│ • Multi-platform│   Prediction    │ • A/B Testing   │ • Dead Letter Queue     │
│ • Template Fill │ • Trend Analysis│ • Performance   │ • Batch Processing      │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DEEPSEEK API LAYER                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│  API Client     │  Cost Manager   │  Cache Layer    │    Monitoring           │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • HTTP Client   │ • Usage Tracking│ • Response Cache│ • API Metrics           │
│ • Retry Logic   │ • Tier Limits   │ • Prompt Cache  │ • Error Tracking        │
│ • Rate Limiting │ • Cost Alerts   │ • Result Cache  │ • Performance Monitor   │
│ • Error Handling│ • Off-peak Sched│ • TTL Management│ • Usage Analytics       │
│ • Circuit Break │ • Budget Control│ • Cache Warming │ • Cost Reporting        │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                        │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   AI Requests   │   Usage Data    │   Cache Store   │    Training Data        │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Request Logs  │ • Token Usage   │ • Redis Cache   │ • User Feedback         │
│ • Response Data │ • Cost Tracking │ • Response Store│ • Content Performance   │
│ • Error Logs    │ • Tier Monitoring│ • Prompt Store │ • Model Improvements    │
│ • Performance   │ • Budget Alerts │ • Result Archive│ • Quality Metrics       │
│ • Quality Score │ • Usage Patterns│ • Cache Stats   │ • A/B Test Results      │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## DeepSeek API Integration

### API Client Implementation

```python
# backend/ai/deepseek_client.py
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('ai.deepseek')

class DeepSeekClient:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = 'https://api.deepseek.com/v1'
        self.session = None
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'ClientNest/1.0'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_content(self, prompt: str, content_type: str = 'post', 
                             platform: str = 'general', **kwargs) -> Dict[str, Any]:
        """Generate content using DeepSeek API"""
        
        # Check rate limits
        if not await self.rate_limiter.acquire():
            raise AIRateLimitError('Rate limit exceeded')
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise AIServiceUnavailableError('Service temporarily unavailable')
        
        try:
            # Build request payload
            payload = self._build_content_payload(prompt, content_type, platform, **kwargs)
            
            # Check cache first
            cache_key = self._generate_cache_key('content', payload)
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f'Cache hit for content generation: {cache_key}')
                return cached_result
            
            # Make API request
            start_time = time.time()
            async with self.session.post(f'{self.base_url}/chat/completions', 
                                       json=payload) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Process and validate response
                    processed_result = self._process_content_response(result, content_type)
                    
                    # Cache successful response
                    cache.set(cache_key, processed_result, timeout=3600)  # 1 hour
                    
                    # Track usage
                    await self._track_usage(payload, result, response_time)
                    
                    # Record success for circuit breaker
                    self.circuit_breaker.record_success()
                    
                    return processed_result
                
                else:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    
                    # Record failure for circuit breaker
                    self.circuit_breaker.record_failure()
                    
                    raise AIAPIError(f'DeepSeek API error: {error_msg}', 
                                   status_code=response.status)
        
        except asyncio.TimeoutError:
            self.circuit_breaker.record_failure()
            raise AITimeoutError('Request timeout')
        
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f'DeepSeek API error: {str(e)}')
            raise
    
    async def analyze_sentiment(self, text: str, context: str = 'comment') -> Dict[str, Any]:
        """Analyze sentiment of text"""
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': f'''
                    You are a sentiment analysis expert. Analyze the sentiment of the given {context}.
                    
                    Return a JSON response with:
                    - sentiment: "positive", "negative", or "neutral"
                    - confidence: float between 0 and 1
                    - emotions: array of detected emotions
                    - urgency: "low", "medium", or "high" (for response priority)
                    - suggested_response_tone: recommended tone for response
                    '''
                },
                {
                    'role': 'user',
                    'content': text
                }
            ],
            'temperature': 0.1,  # Low temperature for consistent analysis
            'max_tokens': 200
        }
        
        cache_key = self._generate_cache_key('sentiment', {'text': text, 'context': context})
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            async with self.session.post(f'{self.base_url}/chat/completions', 
                                       json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    processed_result = self._process_sentiment_response(result)
                    
                    # Cache for 24 hours (sentiment doesn't change)
                    cache.set(cache_key, processed_result, timeout=86400)
                    
                    await self._track_usage(payload, result)
                    return processed_result
                else:
                    raise AIAPIError(f'Sentiment analysis failed: {response.status}')
        
        except Exception as e:
            logger.error(f'Sentiment analysis error: {str(e)}')
            raise
    
    async def optimize_content(self, content: str, platform: str, 
                             optimization_type: str = 'engagement') -> Dict[str, Any]:
        """Optimize content for specific platform and goal"""
        
        optimization_prompts = {
            'engagement': 'Optimize for maximum engagement and interaction',
            'reach': 'Optimize for maximum reach and visibility',
            'conversion': 'Optimize for conversion and call-to-action',
            'brand': 'Optimize for brand consistency and voice'
        }
        
        platform_specs = {
            'twitter': 'Twitter (280 characters, hashtags, mentions)',
            'facebook': 'Facebook (engaging, visual, community-focused)',
            'instagram': 'Instagram (visual-first, hashtags, stories)',
            'linkedin': 'LinkedIn (professional, thought leadership)',
            'tiktok': 'TikTok (trendy, short-form, viral potential)'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': f'''
                    You are a social media optimization expert. {optimization_prompts.get(optimization_type, '')}.
                    
                    Platform: {platform_specs.get(platform, platform)}
                    
                    Return a JSON response with:
                    - optimized_content: the improved content
                    - improvements: array of changes made
                    - hashtags: suggested hashtags (if applicable)
                    - best_posting_time: recommended posting time
                    - engagement_prediction: predicted engagement score (1-10)
                    - call_to_action: suggested CTA (if applicable)
                    '''
                },
                {
                    'role': 'user',
                    'content': f'Original content: {content}'
                }
            ],
            'temperature': 0.7,
            'max_tokens': 500
        }
        
        try:
            async with self.session.post(f'{self.base_url}/chat/completions', 
                                       json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    processed_result = self._process_optimization_response(result)
                    
                    await self._track_usage(payload, result)
                    return processed_result
                else:
                    raise AIAPIError(f'Content optimization failed: {response.status}')
        
        except Exception as e:
            logger.error(f'Content optimization error: {str(e)}')
            raise
    
    def _build_content_payload(self, prompt: str, content_type: str, 
                              platform: str, **kwargs) -> Dict[str, Any]:
        """Build API payload for content generation"""
        
        # Platform-specific instructions
        platform_instructions = {
            'twitter': 'Keep under 280 characters. Use relevant hashtags. Be concise and engaging.',
            'facebook': 'Create engaging content that encourages comments and shares. Use emojis appropriately.',
            'instagram': 'Focus on visual storytelling. Include relevant hashtags. Consider Instagram Stories format.',
            'linkedin': 'Professional tone. Thought leadership content. Industry insights.',
            'tiktok': 'Trendy, fun, and shareable. Consider current trends and challenges.'
        }
        
        # Content type instructions
        content_instructions = {
            'post': 'Create an engaging social media post',
            'caption': 'Write a compelling caption for an image/video',
            'story': 'Create content suitable for Stories format',
            'thread': 'Create a multi-part thread or carousel content'
        }
        
        system_prompt = f'''
        You are an expert social media content creator. 
        
        Task: {content_instructions.get(content_type, 'Create social media content')}
        Platform: {platform}
        Instructions: {platform_instructions.get(platform, 'Create engaging content')}
        
        Additional requirements:
        - Maintain brand voice and tone
        - Include call-to-action when appropriate
        - Optimize for engagement
        - Follow platform best practices
        
        Return a JSON response with:
        - content: the main content/text
        - hashtags: array of relevant hashtags
        - mentions: suggested mentions (if any)
        - call_to_action: suggested CTA
        - posting_tips: array of posting optimization tips
        '''
        
        return {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': kwargs.get('temperature', 0.8),
            'max_tokens': kwargs.get('max_tokens', 800),
            'top_p': kwargs.get('top_p', 0.9)
        }
    
    def _process_content_response(self, response: Dict[str, Any], 
                                content_type: str) -> Dict[str, Any]:
        """Process and validate content generation response"""
        try:
            content = response['choices'][0]['message']['content']
            
            # Try to parse as JSON first
            try:
                parsed_content = json.loads(content)
                if isinstance(parsed_content, dict):
                    return {
                        'content': parsed_content.get('content', content),
                        'hashtags': parsed_content.get('hashtags', []),
                        'mentions': parsed_content.get('mentions', []),
                        'call_to_action': parsed_content.get('call_to_action', ''),
                        'posting_tips': parsed_content.get('posting_tips', []),
                        'usage': response.get('usage', {}),
                        'model': response.get('model', 'deepseek-chat')
                    }
            except json.JSONDecodeError:
                # Fallback to plain text
                pass
            
            # Return plain text response
            return {
                'content': content,
                'hashtags': [],
                'mentions': [],
                'call_to_action': '',
                'posting_tips': [],
                'usage': response.get('usage', {}),
                'model': response.get('model', 'deepseek-chat')
            }
            
        except (KeyError, IndexError) as e:
            raise AIResponseError(f'Invalid response format: {str(e)}')
    
    def _process_sentiment_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process sentiment analysis response"""
        try:
            content = response['choices'][0]['message']['content']
            
            try:
                parsed_result = json.loads(content)
                return {
                    'sentiment': parsed_result.get('sentiment', 'neutral'),
                    'confidence': float(parsed_result.get('confidence', 0.5)),
                    'emotions': parsed_result.get('emotions', []),
                    'urgency': parsed_result.get('urgency', 'low'),
                    'suggested_response_tone': parsed_result.get('suggested_response_tone', 'neutral'),
                    'usage': response.get('usage', {})
                }
            except (json.JSONDecodeError, ValueError):
                # Fallback sentiment analysis
                sentiment = 'neutral'
                if any(word in content.lower() for word in ['positive', 'good', 'great', 'excellent']):
                    sentiment = 'positive'
                elif any(word in content.lower() for word in ['negative', 'bad', 'terrible', 'awful']):
                    sentiment = 'negative'
                
                return {
                    'sentiment': sentiment,
                    'confidence': 0.5,
                    'emotions': [],
                    'urgency': 'low',
                    'suggested_response_tone': 'neutral',
                    'usage': response.get('usage', {})
                }
                
        except (KeyError, IndexError) as e:
            raise AIResponseError(f'Invalid sentiment response: {str(e)}')
    
    def _process_optimization_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process content optimization response"""
        try:
            content = response['choices'][0]['message']['content']
            
            try:
                parsed_result = json.loads(content)
                return {
                    'optimized_content': parsed_result.get('optimized_content', content),
                    'improvements': parsed_result.get('improvements', []),
                    'hashtags': parsed_result.get('hashtags', []),
                    'best_posting_time': parsed_result.get('best_posting_time', ''),
                    'engagement_prediction': float(parsed_result.get('engagement_prediction', 5.0)),
                    'call_to_action': parsed_result.get('call_to_action', ''),
                    'usage': response.get('usage', {})
                }
            except (json.JSONDecodeError, ValueError):
                return {
                    'optimized_content': content,
                    'improvements': [],
                    'hashtags': [],
                    'best_posting_time': '',
                    'engagement_prediction': 5.0,
                    'call_to_action': '',
                    'usage': response.get('usage', {})
                }
                
        except (KeyError, IndexError) as e:
            raise AIResponseError(f'Invalid optimization response: {str(e)}')
    
    def _generate_cache_key(self, operation: str, data: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f'ai_cache:{operation}:{hash_obj.hexdigest()}'
    
    async def _track_usage(self, request_payload: Dict[str, Any], 
                          response: Dict[str, Any], response_time: float = 0):
        """Track API usage for cost monitoring"""
        from .models import AIUsageLog
        
        usage_data = response.get('usage', {})
        
        await AIUsageLog.objects.acreate(
            model=request_payload.get('model', 'deepseek-chat'),
            prompt_tokens=usage_data.get('prompt_tokens', 0),
            completion_tokens=usage_data.get('completion_tokens', 0),
            total_tokens=usage_data.get('total_tokens', 0),
            response_time=response_time,
            request_type=self._get_request_type(request_payload),
            cost=self._calculate_cost(usage_data),
            timestamp=timezone.now()
        )
    
    def _get_request_type(self, payload: Dict[str, Any]) -> str:
        """Determine request type from payload"""
        messages = payload.get('messages', [])
        if messages and len(messages) > 0:
            system_message = messages[0].get('content', '').lower()
            if 'sentiment' in system_message:
                return 'sentiment_analysis'
            elif 'optimize' in system_message:
                return 'content_optimization'
            else:
                return 'content_generation'
        return 'unknown'
    
    def _calculate_cost(self, usage: Dict[str, Any]) -> float:
        """Calculate cost based on token usage"""
        # DeepSeek pricing (example rates)
        prompt_cost_per_1k = 0.0014  # $0.0014 per 1K prompt tokens
        completion_cost_per_1k = 0.0028  # $0.0028 per 1K completion tokens
        
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        
        prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_1k
        completion_cost = (completion_tokens / 1000) * completion_cost_per_1k
        
        return prompt_cost + completion_cost

# Rate Limiter
class RateLimiter:
    def __init__(self, max_requests_per_minute=60):
        self.max_requests = max_requests_per_minute
        self.requests = []
    
    async def acquire(self) -> bool:
        """Acquire rate limit token"""
        now = time.time()
        
        # Remove old requests
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True

# Circuit Breaker
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == 'CLOSED':
            return True
        
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                return True
            return False
        
        if self.state == 'HALF_OPEN':
            return True
        
        return False
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

# Custom Exceptions
class AIError(Exception):
    pass

class AIRateLimitError(AIError):
    pass

class AIServiceUnavailableError(AIError):
    pass

class AIAPIError(AIError):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class AITimeoutError(AIError):
    pass

class AIResponseError(AIError):
    pass
```

### AI Service Layer

```python
# backend/ai/services.py
from typing import Dict, List, Optional, Any
from django.contrib.auth.models import User
from django.utils import timezone
from .deepseek_client import DeepSeekClient
from .models import AIUsageLog, AIRequest, ContentGeneration
from .cost_manager import CostManager
from .queue_manager import AIQueueManager
import asyncio
import logging

logger = logging.getLogger('ai.services')

class AIContentService:
    def __init__(self):
        self.cost_manager = CostManager()
        self.queue_manager = AIQueueManager()
    
    async def generate_post_content(self, user: User, prompt: str, 
                                  platform: str = 'general', **kwargs) -> Dict[str, Any]:
        """Generate social media post content"""
        
        # Check user's AI usage limits
        if not await self.cost_manager.check_usage_limit(user, 'content_generation'):
            raise AIUsageLimitError('AI usage limit exceeded for this billing period')
        
        # Create AI request record
        ai_request = await AIRequest.objects.acreate(
            user=user,
            request_type='content_generation',
            prompt=prompt,
            platform=platform,
            status='pending',
            metadata=kwargs
        )
        
        try:
            # Check if this is a high-priority request
            priority = kwargs.get('priority', 'normal')
            
            if priority == 'high' or user.subscription_tier in ['professional', 'business', 'enterprise']:
                # Process immediately
                result = await self._process_content_generation(ai_request, prompt, platform, **kwargs)
            else:
                # Queue for batch processing
                result = await self.queue_manager.queue_request(ai_request)
            
            return result
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            await ai_request.asave()
            raise
    
    async def _process_content_generation(self, ai_request: AIRequest, 
                                        prompt: str, platform: str, **kwargs) -> Dict[str, Any]:
        """Process content generation request"""
        
        ai_request.status = 'processing'
        ai_request.started_at = timezone.now()
        await ai_request.asave()
        
        try:
            async with DeepSeekClient() as client:
                result = await client.generate_content(
                    prompt=prompt,
                    content_type=kwargs.get('content_type', 'post'),
                    platform=platform,
                    **kwargs
                )
            
            # Save generated content
            content_generation = await ContentGeneration.objects.acreate(
                ai_request=ai_request,
                generated_content=result['content'],
                hashtags=result.get('hashtags', []),
                metadata={
                    'mentions': result.get('mentions', []),
                    'call_to_action': result.get('call_to_action', ''),
                    'posting_tips': result.get('posting_tips', []),
                    'usage': result.get('usage', {})
                }
            )
            
            # Update request status
            ai_request.status = 'completed'
            ai_request.completed_at = timezone.now()
            ai_request.result_id = content_generation.id
            await ai_request.asave()
            
            # Track cost
            await self.cost_manager.track_usage(
                user=ai_request.user,
                request_type='content_generation',
                tokens_used=result.get('usage', {}).get('total_tokens', 0),
                cost=result.get('usage', {}).get('cost', 0)
            )
            
            return {
                'id': content_generation.id,
                'content': result['content'],
                'hashtags': result.get('hashtags', []),
                'mentions': result.get('mentions', []),
                'call_to_action': result.get('call_to_action', ''),
                'posting_tips': result.get('posting_tips', []),
                'request_id': ai_request.id,
                'status': 'completed'
            }
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            ai_request.completed_at = timezone.now()
            await ai_request.asave()
            
            logger.error(f'Content generation failed for request {ai_request.id}: {str(e)}')
            raise
    
    async def analyze_comment_sentiment(self, user: User, comment_text: str, 
                                      context: str = 'comment') -> Dict[str, Any]:
        """Analyze sentiment of a comment"""
        
        if not await self.cost_manager.check_usage_limit(user, 'sentiment_analysis'):
            raise AIUsageLimitError('AI usage limit exceeded for sentiment analysis')
        
        ai_request = await AIRequest.objects.acreate(
            user=user,
            request_type='sentiment_analysis',
            prompt=comment_text,
            status='processing',
            metadata={'context': context}
        )
        
        try:
            async with DeepSeekClient() as client:
                result = await client.analyze_sentiment(comment_text, context)
            
            ai_request.status = 'completed'
            ai_request.completed_at = timezone.now()
            ai_request.metadata.update(result)
            await ai_request.asave()
            
            await self.cost_manager.track_usage(
                user=user,
                request_type='sentiment_analysis',
                tokens_used=result.get('usage', {}).get('total_tokens', 0),
                cost=result.get('usage', {}).get('cost', 0)
            )
            
            return {
                'request_id': ai_request.id,
                'sentiment': result['sentiment'],
                'confidence': result['confidence'],
                'emotions': result.get('emotions', []),
                'urgency': result.get('urgency', 'low'),
                'suggested_response_tone': result.get('suggested_response_tone', 'neutral')
            }
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            await ai_request.asave()
            raise
    
    async def optimize_content(self, user: User, content: str, platform: str, 
                             optimization_type: str = 'engagement') -> Dict[str, Any]:
        """Optimize content for better performance"""
        
        if not await self.cost_manager.check_usage_limit(user, 'content_optimization'):
            raise AIUsageLimitError('AI usage limit exceeded for content optimization')
        
        ai_request = await AIRequest.objects.acreate(
            user=user,
            request_type='content_optimization',
            prompt=content,
            platform=platform,
            status='processing',
            metadata={'optimization_type': optimization_type}
        )
        
        try:
            async with DeepSeekClient() as client:
                result = await client.optimize_content(content, platform, optimization_type)
            
            ai_request.status = 'completed'
            ai_request.completed_at = timezone.now()
            ai_request.metadata.update(result)
            await ai_request.asave()
            
            await self.cost_manager.track_usage(
                user=user,
                request_type='content_optimization',
                tokens_used=result.get('usage', {}).get('total_tokens', 0),
                cost=result.get('usage', {}).get('cost', 0)
            )
            
            return {
                'request_id': ai_request.id,
                'optimized_content': result['optimized_content'],
                'improvements': result.get('improvements', []),
                'hashtags': result.get('hashtags', []),
                'engagement_prediction': result.get('engagement_prediction', 5.0),
                'call_to_action': result.get('call_to_action', '')
            }
            
        except Exception as e:
            ai_request.status = 'failed'
            ai_request.error_message = str(e)
            await ai_request.asave()
            raise
    
    async def get_content_suggestions(self, user: User, topic: str, 
                                    platform: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get multiple content suggestions for a topic"""
        
        suggestions = []
        
        for i in range(count):
            try:
                prompt = f"Create content suggestion #{i+1} about: {topic}"
                result = await self.generate_post_content(
                    user=user,
                    prompt=prompt,
                    platform=platform,
                    temperature=0.8 + (i * 0.1),  # Increase creativity for variety
                    priority='low'  # Use queue for batch processing
                )
                suggestions.append(result)
                
            except Exception as e:
                logger.warning(f'Failed to generate suggestion {i+1}: {str(e)}')
                continue
        
        return suggestions

class AIUsageLimitError(Exception):
    pass
```

### Cost Management System

```python
# backend/ai/cost_manager.py
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
from .models import AIUsageLog, UserAIQuota
import logging

logger = logging.getLogger('ai.cost_manager')

class CostManager:
    # Usage limits by subscription tier (monthly)
    TIER_LIMITS = {
        'free': {
            'content_generation': 10,
            'sentiment_analysis': 50,
            'content_optimization': 5,
            'total_tokens': 10000,
            'monthly_cost_limit': 0.00  # Free tier
        },
        'starter': {
            'content_generation': 100,
            'sentiment_analysis': 500,
            'content_optimization': 50,
            'total_tokens': 100000,
            'monthly_cost_limit': 10.00
        },
        'professional': {
            'content_generation': 500,
            'sentiment_analysis': 2000,
            'content_optimization': 200,
            'total_tokens': 500000,
            'monthly_cost_limit': 50.00
        },
        'business': {
            'content_generation': 2000,
            'sentiment_analysis': 10000,
            'content_optimization': 1000,
            'total_tokens': 2000000,
            'monthly_cost_limit': 200.00
        },
        'enterprise': {
            'content_generation': -1,  # Unlimited
            'sentiment_analysis': -1,
            'content_optimization': -1,
            'total_tokens': -1,
            'monthly_cost_limit': 1000.00
        }
    }
    
    async def check_usage_limit(self, user: User, request_type: str) -> bool:
        """Check if user can make AI request within limits"""
        
        # Get user's subscription tier
        tier = getattr(user, 'subscription_tier', 'free')
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS['free'])
        
        # Check specific request type limit
        type_limit = limits.get(request_type, 0)
        if type_limit == -1:  # Unlimited
            return True
        
        # Get current month usage
        current_usage = await self._get_monthly_usage(user, request_type)
        
        if current_usage >= type_limit:
            logger.warning(f'User {user.id} exceeded {request_type} limit: {current_usage}/{type_limit}')
            return False
        
        # Check total token limit
        token_limit = limits.get('total_tokens', 0)
        if token_limit != -1:
            total_tokens = await self._get_monthly_token_usage(user)
            if total_tokens >= token_limit:
                logger.warning(f'User {user.id} exceeded token limit: {total_tokens}/{token_limit}')
                return False
        
        # Check cost limit
        cost_limit = limits.get('monthly_cost_limit', 0)
        if cost_limit > 0:
            total_cost = await self._get_monthly_cost(user)
            if total_cost >= cost_limit:
                logger.warning(f'User {user.id} exceeded cost limit: ${total_cost:.2f}/${cost_limit:.2f}')
                return False
        
        return True
    
    async def track_usage(self, user: User, request_type: str, 
                         tokens_used: int, cost: float):
        """Track AI usage for billing and limits"""
        
        # Create usage log
        await AIUsageLog.objects.acreate(
            user=user,
            request_type=request_type,
            tokens_used=tokens_used,
            cost=cost,
            timestamp=timezone.now()
        )
        
        # Update cached usage counters
        await self._update_usage_cache(user, request_type, tokens_used, cost)
        
        # Check if approaching limits
        await self._check_usage_warnings(user)
    
    async def _get_monthly_usage(self, user: User, request_type: str) -> int:
        """Get user's monthly usage for specific request type"""
        
        cache_key = f'ai_usage:{user.id}:{request_type}:{timezone.now().strftime("%Y-%m")}'
        cached_usage = cache.get(cache_key)
        
        if cached_usage is not None:
            return cached_usage
        
        # Calculate from database
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        usage_count = await AIUsageLog.objects.filter(
            user=user,
            request_type=request_type,
            timestamp__gte=start_of_month
        ).acount()
        
        # Cache for 1 hour
        cache.set(cache_key, usage_count, 3600)
        
        return usage_count
    
    async def _get_monthly_token_usage(self, user: User) -> int:
        """Get user's total monthly token usage"""
        
        cache_key = f'ai_tokens:{user.id}:{timezone.now().strftime("%Y-%m")}'
        cached_tokens = cache.get(cache_key)
        
        if cached_tokens is not None:
            return cached_tokens
        
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        from django.db.models import Sum
        total_tokens = await AIUsageLog.objects.filter(
            user=user,
            timestamp__gte=start_of_month
        ).aaggregate(total=Sum('tokens_used'))['total'] or 0
        
        cache.set(cache_key, total_tokens, 3600)
        
        return total_tokens
    
    async def _get_monthly_cost(self, user: User) -> float:
        """Get user's total monthly AI cost"""
        
        cache_key = f'ai_cost:{user.id}:{timezone.now().strftime("%Y-%m")}'
        cached_cost = cache.get(cache_key)
        
        if cached_cost is not None:
            return cached_cost
        
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        from django.db.models import Sum
        total_cost = await AIUsageLog.objects.filter(
            user=user,
            timestamp__gte=start_of_month
        ).aaggregate(total=Sum('cost'))['total'] or 0.0
        
        cache.set(cache_key, float(total_cost), 3600)
        
        return float(total_cost)
    
    async def _update_usage_cache(self, user: User, request_type: str, 
                                 tokens_used: int, cost: float):
        """Update cached usage counters"""
        
        month_key = timezone.now().strftime("%Y-%m")
        
        # Update request type counter
        type_cache_key = f'ai_usage:{user.id}:{request_type}:{month_key}'
        current_usage = cache.get(type_cache_key, 0)
        cache.set(type_cache_key, current_usage + 1, 3600)
        
        # Update token counter
        token_cache_key = f'ai_tokens:{user.id}:{month_key}'
        current_tokens = cache.get(token_cache_key, 0)
        cache.set(token_cache_key, current_tokens + tokens_used, 3600)
        
        # Update cost counter
        cost_cache_key = f'ai_cost:{user.id}:{month_key}'
        current_cost = cache.get(cost_cache_key, 0.0)
        cache.set(cost_cache_key, current_cost + cost, 3600)
    
    async def _check_usage_warnings(self, user: User):
        """Check if user is approaching usage limits and send warnings"""
        
        tier = getattr(user, 'subscription_tier', 'free')
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS['free'])
        
        # Check token usage (80% warning)
        token_limit = limits.get('total_tokens', 0)
        if token_limit > 0:
            current_tokens = await self._get_monthly_token_usage(user)
            if current_tokens >= token_limit * 0.8:
                await self._send_usage_warning(user, 'tokens', current_tokens, token_limit)
        
        # Check cost usage (80% warning)
        cost_limit = limits.get('monthly_cost_limit', 0)
        if cost_limit > 0:
            current_cost = await self._get_monthly_cost(user)
            if current_cost >= cost_limit * 0.8:
                await self._send_usage_warning(user, 'cost', current_cost, cost_limit)
    
    async def _send_usage_warning(self, user: User, warning_type: str, 
                                 current_usage: float, limit: float):
        """Send usage warning to user"""
        
        # Check if warning already sent this month
        warning_key = f'ai_warning:{user.id}:{warning_type}:{timezone.now().strftime("%Y-%m")}'
        if cache.get(warning_key):
            return
        
        # Send warning (implement email/notification logic)
        logger.info(f'Sending {warning_type} usage warning to user {user.id}: {current_usage}/{limit}')
        
        # Mark warning as sent
        cache.set(warning_key, True, 86400 * 31)  # Cache for a month
    
    def get_usage_summary(self, user: User) -> Dict[str, Any]:
        """Get user's current usage summary"""
        
        tier = getattr(user, 'subscription_tier', 'free')
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS['free'])
        
        month_key = timezone.now().strftime("%Y-%m")
        
        summary = {
            'tier': tier,
            'limits': limits,
            'current_usage': {},
            'percentage_used': {},
            'remaining': {}
        }
        
        for request_type in ['content_generation', 'sentiment_analysis', 'content_optimization']:
            limit = limits.get(request_type, 0)
            current = cache.get(f'ai_usage:{user.id}:{request_type}:{month_key}', 0)
            
            summary['current_usage'][request_type] = current
            
            if limit == -1:  # Unlimited
                summary['percentage_used'][request_type] = 0
                summary['remaining'][request_type] = -1
            else:
                summary['percentage_used'][request_type] = (current / limit * 100) if limit > 0 else 0
                summary['remaining'][request_type] = max(0, limit - current)
        
        # Token usage
        token_limit = limits.get('total_tokens', 0)
        current_tokens = cache.get(f'ai_tokens:{user.id}:{month_key}', 0)
        
        summary['current_usage']['tokens'] = current_tokens
        if token_limit == -1:
            summary['percentage_used']['tokens'] = 0
            summary['remaining']['tokens'] = -1
        else:
            summary['percentage_used']['tokens'] = (current_tokens / token_limit * 100) if token_limit > 0 else 0
            summary['remaining']['tokens'] = max(0, token_limit - current_tokens)
        
        # Cost usage
        cost_limit = limits.get('monthly_cost_limit', 0)
        current_cost = cache.get(f'ai_cost:{user.id}:{month_key}', 0.0)
        
        summary['current_usage']['cost'] = current_cost
        summary['percentage_used']['cost'] = (current_cost / cost_limit * 100) if cost_limit > 0 else 0
        summary['remaining']['cost'] = max(0, cost_limit - current_cost)
        
        return summary
```

### Queue Management System

```python
# backend/ai/queue_manager.py
import asyncio
import json
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AIRequest
from .deepseek_client import DeepSeekClient
import logging

logger = logging.getLogger('ai.queue')

class AIQueueManager:
    def __init__(self):
        self.queue_key = 'ai_request_queue'
        self.processing_key = 'ai_processing_queue'
        self.max_concurrent = 5  # Maximum concurrent AI requests
        self.batch_size = 10  # Process requests in batches
    
    async def queue_request(self, ai_request: AIRequest) -> Dict[str, Any]:
        """Add request to processing queue"""
        
        # Determine priority
        priority = self._get_request_priority(ai_request)
        
        # Add to queue
        queue_item = {
            'request_id': ai_request.id,
            'priority': priority,
            'queued_at': timezone.now().isoformat(),
            'user_id': ai_request.user.id,
            'request_type': ai_request.request_type
        }
        
        # Use Redis sorted set for priority queue
        import redis
        r = redis.from_url(cache._cache.get_master_client().connection_pool.connection_kwargs['host'])
        
        # Higher score = higher priority
        score = priority * 1000 + (timezone.now().timestamp())
        r.zadd(self.queue_key, {json.dumps(queue_item): score})
        
        ai_request.status = 'queued'
        ai_request.queued_at = timezone.now()
        await ai_request.asave()
        
        # Start processing if not already running
        asyncio.create_task(self._process_queue())
        
        return {
            'request_id': ai_request.id,
            'status': 'queued',
            'estimated_wait_time': await self._estimate_wait_time(priority)
        }
    
    def _get_request_priority(self, ai_request: AIRequest) -> int:
        """Determine request priority based on user tier and request type"""
        
        user_tier = getattr(ai_request.user, 'subscription_tier', 'free')
        
        # Base priority by tier
        tier_priority = {
            'enterprise': 100,
            'business': 80,
            'professional': 60,
            'starter': 40,
            'free': 20
        }
        
        priority = tier_priority.get(user_tier, 20)
        
        # Adjust by request type
        type_priority = {
            'sentiment_analysis': 10,  # Fast processing
            'content_optimization': 5,
            'content_generation': 0
        }
        
        priority += type_priority.get(ai_request.request_type, 0)
        
        # Boost priority for urgent requests
        if ai_request.metadata.get('urgent', False):
            priority += 50
        
        return priority
    
    async def _estimate_wait_time(self, priority: int) -> int:
        """Estimate wait time in seconds based on queue position"""
        
        import redis
        r = redis.from_url(cache._cache.get_master_client().connection_pool.connection_kwargs['host'])
        
        # Count requests with higher or equal priority
        score = priority * 1000 + timezone.now().timestamp()
        queue_position = r.zcount(self.queue_key, score, '+inf')
        
        # Estimate 30 seconds per request
        estimated_seconds = queue_position * 30
        
        return estimated_seconds
    
    async def _process_queue(self):
        """Process queued AI requests"""
        
        # Check if already processing
        if cache.get('ai_queue_processing'):
            return
        
        # Set processing flag
        cache.set('ai_queue_processing', True, timeout=300)  # 5 minutes
        
        try:
            import redis
            r = redis.from_url(cache._cache.get_master_client().connection_pool.connection_kwargs['host'])
            
            while True:
                # Get highest priority requests
                items = r.zrevrange(self.queue_key, 0, self.batch_size - 1, withscores=True)
                
                if not items:
                    break
                
                # Process batch
                tasks = []
                for item_data, score in items:
                    queue_item = json.loads(item_data)
                    task = asyncio.create_task(self._process_request(queue_item))
                    tasks.append(task)
                
                # Wait for batch to complete
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Remove processed items from queue
                for item_data, score in items:
                    r.zrem(self.queue_key, item_data)
                
                # Small delay between batches
                await asyncio.sleep(1)
        
        finally:
            # Clear processing flag
            cache.delete('ai_queue_processing')
    
    async def _process_request(self, queue_item: Dict[str, Any]):
        """Process individual AI request"""
        
        request_id = queue_item['request_id']
        
        try:
            # Get request from database
            ai_request = await AIRequest.objects.aget(id=request_id)
            
            if ai_request.status != 'queued':
                return  # Already processed or cancelled
            
            # Update status
            ai_request.status = 'processing'
            ai_request.started_at = timezone.now()
            await ai_request.asave()
            
            # Process based on request type
            if ai_request.request_type == 'content_generation':
                await self._process_content_generation(ai_request)
            elif ai_request.request_type == 'sentiment_analysis':
                await self._process_sentiment_analysis(ai_request)
            elif ai_request.request_type == 'content_optimization':
                await self._process_content_optimization(ai_request)
            
        except Exception as e:
            logger.error(f'Failed to process AI request {request_id}: {str(e)}')
            
            # Update request with error
            try:
                ai_request = await AIRequest.objects.aget(id=request_id)
                ai_request.status = 'failed'
                ai_request.error_message = str(e)
                ai_request.completed_at = timezone.now()
                await ai_request.asave()
            except:
                pass
    
    async def _process_content_generation(self, ai_request: AIRequest):
        """Process content generation request"""
        
        async with DeepSeekClient() as client:
            result = await client.generate_content(
                prompt=ai_request.prompt,
                content_type=ai_request.metadata.get('content_type', 'post'),
                platform=ai_request.platform or 'general',
                **ai_request.metadata
            )
        
        # Save result
        from .models import ContentGeneration
        content_generation = await ContentGeneration.objects.acreate(
            ai_request=ai_request,
            generated_content=result['content'],
            hashtags=result.get('hashtags', []),
            metadata={
                'mentions': result.get('mentions', []),
                'call_to_action': result.get('call_to_action', ''),
                'posting_tips': result.get('posting_tips', []),
                'usage': result.get('usage', {})
            }
        )
        
        # Update request
        ai_request.status = 'completed'
        ai_request.completed_at = timezone.now()
        ai_request.result_id = content_generation.id
        await ai_request.asave()
    
    async def _process_sentiment_analysis(self, ai_request: AIRequest):
        """Process sentiment analysis request"""
        
        async with DeepSeekClient() as client:
            result = await client.analyze_sentiment(
                ai_request.prompt,
                ai_request.metadata.get('context', 'comment')
            )
        
        # Update request with result
        ai_request.status = 'completed'
        ai_request.completed_at = timezone.now()
        ai_request.metadata.update(result)
        await ai_request.asave()
    
    async def _process_content_optimization(self, ai_request: AIRequest):
        """Process content optimization request"""
        
        async with DeepSeekClient() as client:
            result = await client.optimize_content(
                ai_request.prompt,
                ai_request.platform or 'general',
                ai_request.metadata.get('optimization_type', 'engagement')
            )
        
        # Update request with result
        ai_request.status = 'completed'
        ai_request.completed_at = timezone.now()
        ai_request.metadata.update(result)
        await ai_request.asave()
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        
        import redis
        r = redis.from_url(cache._cache.get_master_client().connection_pool.connection_kwargs['host'])
        
        total_queued = r.zcard(self.queue_key)
        processing_count = await AIRequest.objects.filter(status='processing').acount()
        
        return {
            'total_queued': total_queued,
            'currently_processing': processing_count,
            'is_processing': bool(cache.get('ai_queue_processing')),
            'estimated_processing_time': total_queued * 30  # seconds
        }
```

---

*This AI integration architecture provides a comprehensive, scalable, and cost-effective solution for integrating DeepSeek API into ClientNest, with proper queue management, cost controls, and monitoring capabilities.*