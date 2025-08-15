@echo off
echo Stopping ClientNest User Service...

echo.
echo 1. Stopping Django development server...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr "manage.py"') do (
    echo Killing Python process %%i
    taskkill /pid %%i /f >nul 2>&1
)

echo.
echo 2. Stopping PostgreSQL container...
docker stop clientnest-postgres >nul 2>&1
if %errorlevel% equ 0 (
    echo PostgreSQL container stopped successfully.
) else (
    echo PostgreSQL container was not running or failed to stop.
)

echo.
echo Services stopped successfully!
echo.
pause
