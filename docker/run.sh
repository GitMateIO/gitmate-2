#!/bin/sh

echo "Sleeping for 10s, just in case the database server isn't ready..."
sleep 10

python3 manage.py collectstatic
python3 manage.py migrate
python3 manage.py upmate

gunicorn -b 0.0.0.0:8000 gitmate.wsgi
