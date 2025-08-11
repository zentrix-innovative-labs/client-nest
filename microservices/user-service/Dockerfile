# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=user_service.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script first
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint script executable  
RUN chmod +x /app/entrypoint.sh

# Copy rest of project
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Note: collectstatic will be run in entrypoint.sh after environment is properly set up

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health/ || exit 1

# Command to run the application (avoid entrypoint script issues)
CMD ["bash", "-c", "while ! pg_isready -h $POSTGRES_DB_HOST -p $POSTGRES_DB_PORT -U $POSTGRES_DB_USER; do echo 'Waiting for database...' && sleep 1; done && echo 'Database ready!' && python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8001"]
