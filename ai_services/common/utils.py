import time
from datetime import timedelta, datetime

class RateLimiter:
    """Rate limiter for AI API calls"""
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    async def acquire(self) -> bool:
        now = datetime.now()
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        if len(self.requests) >= self.max_requests:
            return False
        self.requests.append(now)
        return True

class CircuitBreaker:
    """Circuit breaker for AI API calls"""
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def can_execute(self) -> bool:
        if self.state == 'closed':
            return True
        if self.state == 'open':
            if (datetime.now() - self.last_failure_time).seconds >= self.reset_timeout:
                self.state = 'half-open'
                return True
            return False
        return True  # half-open state

    def record_success(self):
        if self.state == 'half-open':
            self.state = 'closed'
        self.failures = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = 'open' 