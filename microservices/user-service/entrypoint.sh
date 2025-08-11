#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h $POSTGRES_DB_HOST -p $POSTGRES_DB_PORT -U $POSTGRES_DB_USER; do
    sleep 1
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@clientnest.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django development server..."
exec "$@"
