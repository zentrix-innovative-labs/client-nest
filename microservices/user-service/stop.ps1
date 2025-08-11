# ClientNest User Service Stop Script for Windows PowerShell
Write-Host "Stopping ClientNest User Service..." -ForegroundColor Red

Write-Host "`n1. Stopping Django development server..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*manage.py runserver*" }
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Host "Killing Python process $($_.Id)" -ForegroundColor Yellow
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "No Django server processes found." -ForegroundColor Yellow
}

Write-Host "`n2. Stopping PostgreSQL container..." -ForegroundColor Yellow
$result = docker stop clientnest-postgres 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL container stopped successfully." -ForegroundColor Green
} else {
    Write-Host "PostgreSQL container was not running or failed to stop." -ForegroundColor Yellow
}

Write-Host "`nServices stopped successfully!" -ForegroundColor Green
Read-Host "`nPress Enter to exit"
