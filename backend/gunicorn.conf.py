# Gunicorn configuration for clientnest.xyz
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "clientnest-backend"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if using SSL termination at load balancer)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Environment variables
raw_env = [
    "DJANGO_SETTINGS_MODULE=config.settings",
    "DJANGO_SECRET_KEY=o(6#7-g6rrr**)(e^oixs_rb$5-!#5=q63sm8@e)_)3ru4ftoq",
    "DEBUG=False",
    "ALLOWED_HOSTS=clientnest.xyz,www.clientnest.xyz,api.clientnest.xyz",
    "SECURE_SSL_REDIRECT=True",
    "SECURE_HSTS_SECONDS=31536000",
    "SECURE_HSTS_INCLUDE_SUBDOMAINS=True",
    "SECURE_HSTS_PRELOAD=True",
    "SESSION_COOKIE_SECURE=True",
    "CSRF_COOKIE_SECURE=True",
] 