# User Service Docker Setup Guide

This guide provides the exact steps to get the User Service running with Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose available

## Current Issues & Solutions

### Issue 1: Entrypoint Script Not Found
**Problem:** `exec /app/entrypoint.sh: no such file or directory`

**Root Cause:** Windows line endings or file permissions

**Solution:** Use CMD instead of ENTRYPOINT in Dockerfile

## Step-by-Step Setup

### 1. Navigate to User Service Directory
```bash
cd "C:\Users\Mark Cole\Desktop\client-nest\microservices\user-service"
```

### 2. Stop Any Running Containers
```bash
docker-compose down -v
```

### 3. Fix the Dockerfile
The Dockerfile should use this approach to avoid entrypoint issues:

```dockerfile
# Command to run the application (avoid entrypoint script issues)
CMD ["bash", "-c", "while ! pg_isready -h $POSTGRES_DB_HOST -p $POSTGRES_DB_PORT -U $POSTGRES_DB_USER; do echo 'Waiting for database...' && sleep 1; done && echo 'Database ready!' && python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8001"]
```

### 4. Build the Docker Image
```bash
docker-compose build --no-cache user-service
```

### 5. Start the Services
```bash
docker-compose up -d
```

### 6. Verify Services Are Running
```bash
docker-compose ps
```

**Expected Output:**
```
NAME                 IMAGE         COMMAND                  SERVICE   CREATED          STATUS                    PORTS
clientnest-user-db   postgres:15   "docker-entrypoint.s…"   user-db   X minutes ago    Up X minutes (healthy)   0.0.0.0:5433->5432/tcp
clientnest-user-service user-service-user-service "bash -c 'while ! p…" user-service X minutes ago Up X minutes 0.0.0.0:8001->8001/tcp
```

### 7. Check Application Logs
```bash
docker-compose logs user-service
```

**Expected Output:**
```
clientnest-user-service  | Waiting for database...
clientnest-user-service  | Database ready!
clientnest-user-service  | Operations to perform: ...
clientnest-user-service  | Running migrations: ...
clientnest-user-service  | Watching for file changes with StatReloader
clientnest-user-service  | Performing system checks...
clientnest-user-service  | System check identified no issues (0 silenced).
clientnest-user-service  | August 07, 2025 - XX:XX:XX
clientnest-user-service  | Django version X.X.X, using settings 'user_service.settings'
clientnest-user-service  | Starting development server at http://0.0.0.0:8001/
clientnest-user-service  | Quit the server with CONTROL-C.
```

### 8. Test the API
The service should be accessible at: `http://localhost:8001`

Test endpoints:
- Health check: `http://localhost:8001/health/`
- API docs: `http://localhost:8001/api/docs/` (if available)
- Registration: `http://localhost:8001/api/v1/users/auth/register/`
- Login: `http://localhost:8001/api/v1/users/auth/login/`

## Troubleshooting

### Container Keeps Exiting
1. Check logs: `docker-compose logs user-service`
2. Check if database is ready: `docker-compose logs user-db`
3. Rebuild without cache: `docker-compose build --no-cache`

### Port Conflicts
- User service runs on port `8001` (mapped from container port 8001)
- Database runs on port `5433` (mapped from container port 5432)

### Database Connection Issues
- Verify database container is healthy: `docker-compose ps`
- Check environment variables in docker-compose.yml match

## Quick Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop services and remove volumes
docker-compose down -v

# View logs
docker-compose logs

# View specific service logs
docker-compose logs user-service
docker-compose logs user-db

# Rebuild specific service
docker-compose build --no-cache user-service

# Enter container shell
docker-compose exec user-service bash

# Run Django commands
docker-compose exec user-service python manage.py migrate
docker-compose exec user-service python manage.py createsuperuser
```

## Current Configuration

### Port Mapping
- **User Service:** `localhost:8001` → `container:8001`
- **Database:** `localhost:5433` → `container:5432`

### Environment Variables
```env
DEBUG=True
SECRET_KEY=django-insecure-user-service-key-change-in-production
POSTGRES_DB_NAME=client-nest
POSTGRES_DB_USER=postgres
POSTGRES_DB_PASSWORD=markCole256
POSTGRES_DB_HOST=user-db
POSTGRES_DB_PORT=5432
USE_SQLITE=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,user-service
```

### Testing URLs
Update your test scripts to use port `8001` instead of `8000`:
- Registration: `http://127.0.0.1:8001/api/v1/users/auth/register/`
- Login: `http://127.0.0.1:8001/api/v1/users/auth/login/`
