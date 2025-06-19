class AIBaseException(Exception):
    """Base exception for AI-related errors"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

class AIRateLimitError(AIBaseException):
    """Exception raised when AI API rate limit is exceeded"""
    def __init__(self, message: str = 'Rate limit exceeded'):
        super().__init__(message, status_code=429)

class AIServiceUnavailableError(AIBaseException):
    """Exception raised when AI service is temporarily unavailable"""
    def __init__(self, message: str = 'Service temporarily unavailable'):
        super().__init__(message, status_code=503)

class AIAPIError(AIBaseException):
    """Exception raised when AI API returns an error"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code=status_code)

class AITimeoutError(AIBaseException):
    """Exception raised when AI API request times out"""
    def __init__(self, message: str = 'Request timeout'):
        super().__init__(message, status_code=504)

class AIValidationError(AIBaseException):
    """Exception raised when input validation fails"""
    def __init__(self, message: str = 'Invalid input'):
        super().__init__(message, status_code=400)

class AIAuthenticationError(AIBaseException):
    """Exception raised when API authentication fails"""
    def __init__(self, message: str = 'Authentication failed'):
        super().__init__(message, status_code=401)

class AIQuotaExceededError(AIBaseException):
    """Exception raised when user quota is exceeded"""
    def __init__(self, message: str = 'Quota exceeded'):
        super().__init__(message, status_code=402)

class AIContentFilterError(AIBaseException):
    """Exception raised when content violates content policy"""
    def __init__(self, message: str = 'Content policy violation'):
        super().__init__(message, status_code=422)

class AIInvalidResponseError(AIBaseException):
    """Exception raised when AI response is invalid or unexpected"""
    def __init__(self, message: str = 'Invalid AI response'):
        super().__init__(message, status_code=502)