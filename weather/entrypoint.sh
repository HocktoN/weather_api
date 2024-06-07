#!/bin/sh

sleep 5

# Django veritabanı migrasyonlarını çalıştır
python manage.py migrate --noinput

# Django statik dosyalarını klasör acıp toplar
python manage.py collectstatic --noinput

# Gunicorn ile uygulamayı başlat
gunicorn --bind 0.0.0.0:8000 weather.wsgi:application
