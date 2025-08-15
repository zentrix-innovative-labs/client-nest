# ClientNest User Service Docker Setup

This document explains how to run the ClientNest User Service using Docker on **Windows**, **macOS**, and **Linux**.

## 📋 Prerequisites

### All Operating Systems
- **Docker Desktop** installed and running
- **Python 3.8+** installed
- **Git** (for cloning the repository)

### Platform-Specific Requirements

**Windows:**
- Windows 10/11 with WSL2 enabled (recommended)
- PowerShell 5.1+ or Windows Terminal
- Python added to PATH environment variable

**macOS:**
- macOS 10.14+ (Mojave or later)
- Homebrew (recommended for Python installation)
- Terminal or iTerm2

**Linux:**
- Ubuntu 18.04+, CentOS 7+, or equivalent
- Docker CE installed
- Python 3.8+ with pip

### Installation Links
- **Docker Desktop**: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- **Python**: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Git**: [https://git-scm.com/downloads](https://git-scm.com/downloads)

## 🚀 Quick Start

### Option 1: Simple Start (Recommended)

**macOS/Linux:**
```bash
./start.sh
```

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Windows (Command Prompt):**
```cmd
start.bat
```

### Option 2: Manual Docker Commands

1. **Start PostgreSQL Database:**

**macOS/Linux:**
```bash
docker run --name clientnest-postgres \
  -e POSTGRES_PASSWORD=markCole256 \
  -e POSTGRES_DB=client-nest \
  -e POSTGRES_USER=postgres \
  -p 5433:5432 \
  -d postgres:15-alpine
```

**Windows (PowerShell):**
```powershell
docker run --name clientnest-postgres `
  -e POSTGRES_PASSWORD=markCole256 `
  -e POSTGRES_DB=client-nest `
  -e POSTGRES_USER=postgres `
  -p 5433:5432 `
  -d postgres:15-alpine
```

**Windows (Command Prompt):**
```cmd
docker run --name clientnest-postgres ^
  -e POSTGRES_PASSWORD=markCole256 ^
  -e POSTGRES_DB=client-nest ^
  -e POSTGRES_USER=postgres ^
  -p 5433:5432 ^
  -d postgres:15-alpine
```

2. **Run Migrations:**

**macOS/Linux:**
```bash
python3 manage.py migrate
```

**Windows:**
```cmd
python manage.py migrate
```

3. **Start Django Server:**

**macOS/Linux:**
```bash
python3 manage.py runserver 8001
```

**Windows:**
```cmd
python manage.py runserver 8001
```

## 🛑 Stopping Services

**macOS/Linux:**
```bash
./stop.sh
```

**Windows (PowerShell):**
```powershell
.\stop.ps1
```

**Windows (Command Prompt):**
```cmd
stop.bat
```

Or manually:

**macOS/Linux:**
```bash
# Stop Django server
pkill -f "python.*manage.py runserver"

# Stop PostgreSQL container
docker stop clientnest-postgres
```

**Windows (PowerShell):**
```powershell
# Stop Django server
Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*manage.py runserver*"} | Stop-Process -Force

# Stop PostgreSQL container
docker stop clientnest-postgres
```

**Windows (Command Prompt):**
```cmd
# Stop Django server
taskkill /f /im python.exe

# Stop PostgreSQL container
docker stop clientnest-postgres
```

## 🐳 Docker Configuration

### Current Setup
- **Database**: PostgreSQL 15 (Alpine) running in Docker container
- **Application**: Django development server running locally
- **Database Port**: 5433 (mapped from container port 5432)
- **Application Port**: 8001

### Environment Variables
The application uses the following environment variables (defined in `.env`):

```env
DEBUG=True
POSTGRES_DB_NAME=client-nest
POSTGRES_DB_USER=postgres
POSTGRES_DB_PASSWORD=markCole256
POSTGRES_DB_HOST=localhost
POSTGRES_DB_PORT=5433
USE_SQLITE=False
```

## 📚 Available Endpoints

- **Main Application**: http://127.0.0.1:8001/
- **Admin Interface**: http://127.0.0.1:8001/admin/ 
  - Username: `markcole`
  - Password: `admin123`
- **API Documentation**: http://127.0.0.1:8001/swagger/
- **API Endpoints**: http://127.0.0.1:8001/api/v1/

### Key API Endpoints
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/users/me/` - Get current user profile
- `GET /api/v1/profiles/` - User profiles
- `GET /api/v1/health/` - Health check

## 🔧 Development Commands

### Database Operations

**macOS/Linux:**
```bash
# Run migrations
python3 manage.py migrate

# Create migrations
python3 manage.py makemigrations

# Create superuser
python3 manage.py createsuperuser

# Access database shell
docker exec -it clientnest-postgres psql -U postgres -d client-nest
```

**Windows:**
```cmd
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Access database shell
docker exec -it clientnest-postgres psql -U postgres -d client-nest
```

### Virtual Environment Setup

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### Docker Operations
```bash
# View running containers
docker ps

# View logs from PostgreSQL container
docker logs clientnest-postgres

# Stop and remove PostgreSQL container
docker stop clientnest-postgres
docker rm clientnest-postgres

# Remove PostgreSQL volume (⚠️ This will delete all data!)
docker volume rm $(docker volume ls -q | grep postgres)
```

## 🏗️ Full Docker Compose Setup (Alternative)

If you prefer to run everything in containers, you can use Docker Compose:

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔍 Troubleshooting

### Common Issues

1. **Port 5433 already in use:**
   
   **macOS/Linux:**
   ```bash
   # Find what's using the port
   lsof -i :5433
   
   # Stop the conflicting process or use a different port
   ```
   
   **Windows:**
   ```cmd
   # Find what's using the port
   netstat -ano | findstr :5433
   
   # Kill the process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

2. **PostgreSQL connection failed:**
   ```bash
   # Check if container is running
   docker ps | grep postgres
   
   # Check container logs
   docker logs clientnest-postgres
   ```

3. **Django migration errors:**
   
   **macOS/Linux:**
   ```bash
   # Reset migrations (⚠️ Development only!)
   python3 manage.py migrate --fake-initial
   ```
   
   **Windows:**
   ```cmd
   # Reset migrations (⚠️ Development only!)
   python manage.py migrate --fake-initial
   ```

4. **Permission denied on scripts:**
   
   **macOS/Linux:**
   ```bash
   chmod +x start.sh stop.sh
   ```
   
   **Windows (PowerShell):**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

5. **Python not found error:**
   
   **Windows:** Make sure Python is installed and added to PATH. Download from [python.org](https://www.python.org/downloads/windows/)
   
   **macOS:** Install Python via Homebrew: `brew install python`

## 📁 Project Structure

```
user-service/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Docker ignore file
├── entrypoint.sh           # Container entrypoint script (Linux/macOS)
├── start.sh               # Quick start script (Linux/macOS)
├── start.bat              # Quick start script (Windows CMD)
├── start.ps1              # Quick start script (Windows PowerShell)
├── stop.sh                # Quick stop script (Linux/macOS)
├── stop.bat               # Quick stop script (Windows CMD)
├── stop.ps1               # Quick stop script (Windows PowerShell)
├── .env                   # Environment variables
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── user_service/          # Django project
    ├── settings.py        # Django settings
    └── ...
```

## 🎯 Next Steps

1. **Production Deployment**: Use Docker Compose or Kubernetes for production
2. **SSL/TLS**: Add HTTPS support with reverse proxy (nginx)
3. **Monitoring**: Add logging, monitoring, and health checks
4. **Backup**: Set up automated database backups
5. **Scaling**: Use multiple Django instances behind a load balancer
