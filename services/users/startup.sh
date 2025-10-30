#!/bin/bash

echo "🚀 Starting backend service..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! pg_isready -h db -p 5432 -U postgres > /dev/null 2>&1; do
    echo "   Database not ready, waiting..."
    sleep 2
done
echo "✅ Database is ready!"

# Wait a bit more for database to fully initialize
sleep 3

# Initialize Alembic if not already done
echo "📦 Initializing database migrations..."
cd /usr/src/app
if [ ! -d "migrations/versions" ]; then
    python manage.py db init || echo "⚠️  Migrations already initialized"
fi

# Create initial migration if needed
if [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
    echo "📝 Creating initial migration..."
    python manage.py db migrate -m "Initial migration" || echo "⚠️  Migration creation skipped"
fi

# Run database migrations
echo "⬆️  Running database migrations..."
python manage.py db upgrade || echo "⚠️  No migrations to run"

# Seed initial data
echo "🌱 Seeding initial data..."
python manage.py seed_db || echo "⚠️  Seeding skipped"

# Start the Flask application
echo "🎯 Starting Flask application on port 5001..."
exec gunicorn -b 0.0.0.0:5001 --workers 4 --timeout 120 --access-logfile - --error-logfile - "project:create_app()"

