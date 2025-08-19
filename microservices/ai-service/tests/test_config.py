"""
Test configuration management for AI service tests.
Makes timeout values configurable via environment variables as suggested by Copilot AI.
"""

import os
from typing import Dict, Any


class TestTimeoutConfig:
    """
    Configurable timeout values for different test scenarios.
    
    Timeout values can be overridden via environment variables:
    - TEST_HEALTH_TIMEOUT: Timeout for health checks (default: 5s)
    - TEST_STANDARD_TIMEOUT: Timeout for regular API calls (default: 15s)
    - TEST_AI_GENERATION_TIMEOUT: Timeout for AI operations (default: 30s)
    - TEST_DEFAULT_TIMEOUT: Default timeout fallback (default: 10s)
    
    Environment variables allow different timeout configurations for:
    - Development: Faster feedback with shorter timeouts
    - CI/CD: Balanced timeouts for automated testing
    - Production-like: Longer timeouts for realistic scenarios
    """
    
    # Default timeout values (in seconds)
    DEFAULT_HEALTH_TIMEOUT = 5
    DEFAULT_STANDARD_TIMEOUT = 15
    DEFAULT_AI_GENERATION_TIMEOUT = 30
    DEFAULT_DEFAULT_TIMEOUT = 10
    
    @classmethod
    def get_health_timeout(cls) -> int:
        """Get timeout for health checks (fast operations)"""
        return int(os.getenv('TEST_HEALTH_TIMEOUT', cls.DEFAULT_HEALTH_TIMEOUT))
    
    @classmethod
    def get_standard_timeout(cls) -> int:
        """Get timeout for regular API operations"""
        return int(os.getenv('TEST_STANDARD_TIMEOUT', cls.DEFAULT_STANDARD_TIMEOUT))
    
    @classmethod
    def get_ai_generation_timeout(cls) -> int:
        """Get timeout for AI operations (can be slow)"""
        return int(os.getenv('TEST_AI_GENERATION_TIMEOUT', cls.DEFAULT_AI_GENERATION_TIMEOUT))
    
    @classmethod
    def get_default_timeout(cls) -> int:
        """Get default timeout fallback"""
        return int(os.getenv('TEST_DEFAULT_TIMEOUT', cls.DEFAULT_DEFAULT_TIMEOUT))
    
    @classmethod
    def get_all_timeouts(cls) -> Dict[str, int]:
        """Get all timeout values as a dictionary"""
        return {
            'health': cls.get_health_timeout(),
            'standard': cls.get_standard_timeout(),
            'ai_generation': cls.get_ai_generation_timeout(),
            'default': cls.get_default_timeout(),
        }
    
    @classmethod
    def get_timeout_for_endpoint(cls, endpoint_path: str) -> int:
        """
        Get appropriate timeout based on endpoint type.
        
        Args:
            endpoint_path: The endpoint path to determine timeout for
            
        Returns:
            Appropriate timeout value in seconds
        """
        # Health endpoints get fast timeout
        if 'health' in endpoint_path:
            return cls.get_health_timeout()
        
        # AI generation endpoints get longer timeout
        if any(keyword in endpoint_path for keyword in ['generate', 'analyze', 'optimize', 'schedule']):
            return cls.get_ai_generation_timeout()
        
        # Regular API endpoints get standard timeout
        return cls.get_standard_timeout()


class TestEnvironmentConfig:
    """
    Environment-specific test configuration.
    """
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return os.getenv('TEST_ENVIRONMENT', 'development').lower() == 'development'
    
    @classmethod
    def is_ci_cd(cls) -> bool:
        """Check if running in CI/CD environment"""
        return os.getenv('CI', 'false').lower() == 'true' or os.getenv('TEST_ENVIRONMENT', '').lower() == 'ci'
    
    @classmethod
    def is_production_like(cls) -> bool:
        """Check if running in production-like environment"""
        return os.getenv('TEST_ENVIRONMENT', '').lower() == 'production'
    
    @classmethod
    def get_environment_name(cls) -> str:
        """Get current test environment name"""
        if cls.is_ci_cd():
            return 'ci_cd'
        elif cls.is_production_like():
            return 'production_like'
        else:
            return 'development'
    
    @classmethod
    def get_recommended_timeouts(cls) -> Dict[str, int]:
        """
        Get recommended timeout values for current environment.
        
        Returns:
            Dictionary of recommended timeout values
        """
        if cls.is_production_like():
            # Production-like: More realistic timeouts
            return {
                'health': 10,
                'standard': 30,
                'ai_generation': 60,
                'default': 30,
            }
        elif cls.is_ci_cd():
            # CI/CD: Balanced timeouts
            return {
                'health': 10,
                'standard': 20,
                'ai_generation': 45,
                'default': 20,
            }
        else:
            # Development: Fast feedback
            return {
                'health': 5,
                'standard': 15,
                'ai_generation': 30,
                'default': 10,
            }


def print_timeout_configuration():
    """Print current timeout configuration for debugging"""
    print("=== Test Timeout Configuration ===")
    print(f"Environment: {TestEnvironmentConfig.get_environment_name()}")
    print("Current timeouts:")
    for name, value in TestTimeoutConfig.get_all_timeouts().items():
        print(f"  {name}: {value}s")
    
    print("\nRecommended timeouts for current environment:")
    for name, value in TestEnvironmentConfig.get_recommended_timeouts().items():
        print(f"  {name}: {value}s")
    
    print("\nEnvironment variables to override timeouts:")
    print("  TEST_HEALTH_TIMEOUT")
    print("  TEST_STANDARD_TIMEOUT") 
    print("  TEST_AI_GENERATION_TIMEOUT")
    print("  TEST_DEFAULT_TIMEOUT")
    print("  TEST_ENVIRONMENT (development/ci/production_like)")
    print("===============================================")


if __name__ == "__main__":
    # Print configuration when run directly
    print_timeout_configuration()
