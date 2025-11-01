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

# Create database views
echo "📊 Creating database views..."
psql $DATABASE_URL -c "
CREATE OR REPLACE VIEW member_profile_complete AS
SELECT
    gm.id,
    gm.group_id,
    gm.user_id,
    gm.first_name,
    gm.last_name,
    gm.email,
    gm.phone_number,
    gm.id_number,
    gm.date_of_birth,
    gm.gender,
    gm.occupation,
    gm.status,
    gm.joined_date,
    gm.is_active,
    gm.role,
    gm.share_balance,
    gm.total_contributions,
    gm.attendance_percentage,
    gm.is_eligible_for_loans,
    gm.target_amount,
    gm.profile_photo_url,
    gm.created_date,
    gm.updated_date,
    sg.name as group_name,
    sg.district as group_district,
    sg.parish as group_parish,
    sg.village as group_village,
    sg.formation_date as group_formation_date
FROM group_members gm
LEFT JOIN savings_groups sg ON gm.group_id = sg.id;
" || echo "⚠️  View creation skipped"

# Add missing columns to group_documents table
echo "📝 Updating group_documents table schema..."
psql $DATABASE_URL -c "
ALTER TABLE group_documents
ADD COLUMN IF NOT EXISTS is_compressed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS compressed_size INTEGER,
ADD COLUMN IF NOT EXISTS compression_ratio NUMERIC(5, 2),
ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64),
ADD COLUMN IF NOT EXISTS thumbnail_path VARCHAR(500),
ADD COLUMN IF NOT EXISTS preview_path VARCHAR(500),
ADD COLUMN IF NOT EXISTS has_preview BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS parent_document_id INTEGER,
ADD COLUMN IF NOT EXISTS replaced_by_id INTEGER,
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS file_category VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_filename VARCHAR(255),
ADD COLUMN IF NOT EXISTS download_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_accessed TIMESTAMP,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS deleted_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS deleted_by INTEGER,
ADD COLUMN IF NOT EXISTS version VARCHAR(20),
ADD COLUMN IF NOT EXISTS is_current_version BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS access_level VARCHAR(50) DEFAULT 'GROUP';
" || echo "⚠️  Schema update skipped"

# Seed initial data
echo "🌱 Seeding initial data..."
python manage.py seed_db || echo "⚠️  Admin seeding skipped"

# Check if comprehensive data should be seeded (only on first run)
if [ ! -f "/usr/src/app/.data_seeded" ]; then
    echo "🌱 First run detected - seeding comprehensive demo data..."
    python manage.py seed_demo_data && touch /usr/src/app/.data_seeded || echo "⚠️  Demo data seeding skipped"
else
    echo "ℹ️  Demo data already seeded (delete /usr/src/app/.data_seeded to reseed)"
fi

# Start the Flask application
echo "🎯 Starting Flask application on port 5001..."
exec gunicorn -b 0.0.0.0:5001 --workers 4 --timeout 120 --access-logfile - --error-logfile - "project:create_app()"

