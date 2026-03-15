#!/bin/bash

# Startup script for Render deployment
# Runs migrations before starting the server

echo "🚀 Starting PED Majevica Backend..."

# Run database migrations
echo "📦 Running database migrations..."
flask db upgrade

# Optional: Run JSON data migration (only if needed)
if [ -f "migrate_json_to_db.py" ]; then
    echo "📥 Migrating JSON data to database..."
    python migrate_json_to_db.py
fi

# NOTE: Admin users are now created automatically via init_admin() in app/__init__.py
# No need to run create_admin_simple.py manually

# Seed trails and events (run only if script exists)
if [ -f "seed_trails_events.py" ]; then
    echo "🌲 Seeding trails and events..."
    python seed_trails_events.py
fi

# Start Gunicorn server
echo "🌐 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app
