#!/bin/sh

sleep 5

python manage.py migrate --noinput

python manage.py collectstatic --noinput

gunicorn --bind 0.0.0.0:8000 weather.wsgi:application
