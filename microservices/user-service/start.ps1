# ClientNest User Service Startup Script for Windows PowerShell
Write-Host "Starting ClientNest User Service..." -ForegroundColor Green

Write-Host "`n1. Checking if PostgreSQL container exists..." -ForegroundColor Yellow
$containerExists = docker ps -a --filter "name=clientnest-postgres" --format "{{.Names}}" | Select-String "clientnest-postgres"

if (-not $containerExists) {
    Write-Host "Creating new PostgreSQL container..." -ForegroundColor Yellow
    docker run --name clientnest-postgres `
        -e POSTGRES_PASSWORD=markCole256 `
        -e POSTGRES_DB=client-nest `
        -e POSTGRES_USER=postgres `
        -p 5433:5432 `
        -d postgres:15-alpine
} else {
    Write-Host "Starting existing PostgreSQL container..." -ForegroundColor Yellow
    docker start clientnest-postgres
}

Write-Host "`n2. Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n3. Checking PostgreSQL connection..." -ForegroundColor Yellow
do {
    $pgReady = docker exec clientnest-postgres pg_isready -U postgres -d client-nest 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PostgreSQL not ready yet, waiting..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
} while ($LASTEXITCODE -ne 0)

Write-Host "PostgreSQL is ready!" -ForegroundColor Green

Write-Host "`n4. Activating virtual environment and running migrations..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
    python manage.py migrate
} else {
    Write-Host "Virtual environment not found. Please run:" -ForegroundColor Red
    Write-Host "python -m venv venv" -ForegroundColor Red
    Write-Host "Then install dependencies: pip install -r requirements.txt" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n5. Starting Django development server..." -ForegroundColor Yellow
Write-Host "Server will be available at: http://127.0.0.1:8001/" -ForegroundColor Green
Write-Host "Admin panel: http://127.0.0.1:8001/admin/ (markcole/admin123)" -ForegroundColor Green
Write-Host "API docs: http://127.0.0.1:8001/swagger/" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Cyan

python manage.py runserver 8001
