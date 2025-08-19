import os

def validate_config():
    """Validate critical configuration settings"""
    required_vars = [
        'DEEPSEEK_API_KEY',
        'SECRET_KEY',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT'
    ]
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 