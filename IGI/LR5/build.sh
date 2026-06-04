#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py migrate --noinput

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

python manage.py collectstatic --noinput
