#!/bin/sh
set -e

pip install -r requirements.txt

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

if [ "$DJANGO_CREATE_SUPERUSER" = "True" ]; then
    python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not username or not email or not password:
    raise SystemExit('DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD are required')

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.email = email
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

print(f'Superuser {username} created/updated successfully')
"
fi