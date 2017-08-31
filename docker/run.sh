#!/bin/sh

. ./docker/common.sh

echo "Sleeping for 10s, just in case the database server isn't ready..."
sleep 10

echo "Collecting static files ..."
python3 manage.py collectstatic --noinput

echo "Migrating database ..."
python3 manage.py migrate

echo "Migrating plugins ..."
python3 manage.py upmate

# For debugging: python3 manage.py runserver 0.0.0.0:8000
exec gunicorn gitmate.wsgi \
    --name=gitmate \
    --workers=$NUM_WORKERS \
    --user=$USER --group=$USER \
    --timeout=$TIMEOUT \
    --bind=0.0.0.0:8000 \
    --log-level=$LOG_LEVEL \
    --log-file=- \
    --worker-class=gevent
