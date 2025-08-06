@echo off
echo Starting ClientNest User Service...

echo.
echo 1. Checking if PostgreSQL container exists...
docker ps -a | findstr clientnest-postgres >nul
if %errorlevel% neq 0 (
    echo Creating new PostgreSQL container...
    docker run --name clientnest-postgres -e POSTGRES_PASSWORD=markCole256 -e POSTGRES_DB=client-nest -e POSTGRES_USER=postgres -p 5433:5432 -d postgres:15-alpine
) else (
    echo Starting existing PostgreSQL container...
    docker start clientnest-postgres
)

echo.
echo 2. Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak >nul

echo.
echo 3. Checking PostgreSQL connection...
:check_postgres
docker exec clientnest-postgres pg_isready -U postgres -d client-nest >nul 2>&1
if %errorlevel% neq 0 (
    echo PostgreSQL not ready yet, waiting...
    timeout /t 2 /nobreak >nul
    goto check_postgres
)
echo PostgreSQL is ready!

echo.
echo 4. Activating virtual environment and running migrations...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python manage.py migrate
) else (
    echo Virtual environment not found. Please run: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo 5. Starting Django development server...
echo Server will be available at: http://127.0.0.1:8001/
echo Admin panel: http://127.0.0.1:8001/admin/ (markcole/admin123)
echo API docs: http://127.0.0.1:8001/swagger/
echo.
echo Press Ctrl+C to stop the server
python manage.py runserver 8001
