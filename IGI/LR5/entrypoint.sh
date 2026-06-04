#!/bin/sh
set -e

python manage.py wait_for_db
python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "$DJANGO_LOAD_DEMO_DATA" = "True" ]; then
    SEED_ARGS=""
    if [ "$DJANGO_CREATE_DEMO_USERS" = "True" ]; then
        SEED_ARGS="$SEED_ARGS --with-demo-users"
    fi
    if [ "$DJANGO_CREATE_DEMO_ADMIN" = "True" ]; then
        SEED_ARGS="$SEED_ARGS --with-demo-admin"
    fi
    python manage.py seed_data $SEED_ARGS
fi

exec gunicorn realty_project.wsgi:application --bind 0.0.0.0:8000
