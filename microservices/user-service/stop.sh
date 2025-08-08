#!/bin/bash

# ClientNest User Service Stop Script
# This script stops the Django server and PostgreSQL container

echo "🛑 Stopping ClientNest User Service..."

# Stop Django development server
echo "🐍 Stopping Django development server..."
pkill -f "python.*manage.py runserver" 2>/dev/null || echo "No Django server running"

# Stop PostgreSQL container
echo "🐘 Stopping PostgreSQL container..."
if docker ps --format "table {{.Names}}" | grep -q "clientnest-postgres"; then
    docker stop clientnest-postgres
    echo "✅ PostgreSQL container stopped"
else
    echo "ℹ️  PostgreSQL container was not running"
fi

echo "✅ All services stopped!"
echo ""
echo "To restart, run: ./start.sh"
