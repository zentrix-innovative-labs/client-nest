#!/bin/bash

# ClientNest User Service Startup Script
# This script starts the PostgreSQL database and Django user service

set -e

echo "🚀 Starting ClientNest User Service..."

# Function to check if PostgreSQL container is running
check_postgres() {
    if docker ps --format "table {{.Names}}" | grep -q "clientnest-postgres"; then
        echo "✅ PostgreSQL container is already running"
        return 0
    else
        return 1
    fi
}

# Function to start PostgreSQL container
start_postgres() {
    echo "🐘 Starting PostgreSQL container..."
    if docker run --name clientnest-postgres \
        -e POSTGRES_PASSWORD=markCole256 \
        -e POSTGRES_DB=client-nest \
        -e POSTGRES_USER=postgres \
        -p 5433:5432 \
        -d postgres:15-alpine; then
        echo "✅ PostgreSQL container started successfully"
        
        # Wait for PostgreSQL to be ready
        echo "⏳ Waiting for PostgreSQL to be ready..."
        sleep 5
        
        # Check if we can connect
        until docker exec clientnest-postgres pg_isready -U postgres; do
            echo "Waiting for PostgreSQL..."
            sleep 2
        done
        echo "✅ PostgreSQL is ready!"
    else
        echo "⚠️  PostgreSQL container already exists, starting it..."
        docker start clientnest-postgres
    fi
}

# Function to start Django development server
start_django() {
    echo "🐍 Starting Django development server..."
    
    # Set up environment
    export PYTHONPATH=/Users/markcolemukisa/clientnest2.0/microservices/user-service/venv/lib/python3.13/site-packages:$PYTHONPATH
    
    cd /Users/markcolemukisa/clientnest2.0/microservices/user-service
    
    # Run migrations
    echo "📦 Running database migrations..."
    python3 manage.py migrate
    
    # Start server
    echo "🌐 Starting development server on http://127.0.0.1:8001"
    echo "📚 Admin interface: http://127.0.0.1:8001/admin/ (admin/admin123)"
    echo "📖 API docs: http://127.0.0.1:8001/swagger/"
    echo ""
    echo "Press Ctrl+C to stop the server"
    
    python3 manage.py runserver 8001
}

# Main execution
main() {
    # Check if PostgreSQL is running, start it if not
    if ! check_postgres; then
        start_postgres
    fi
    
    # Start Django server
    start_django
}

# Run main function
main "$@"
