#!/bin/bash
set -e

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding demo users..."
python manage.py seed_users 2>/dev/null || true

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

PORT="${PORT:-8000}"
echo "==> Starting gunicorn on 0.0.0.0:${PORT}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WEB_WORKERS:-2}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
