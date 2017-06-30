#!/bin/sh

exec celery beat \
            -A gitmate \
	    --uid=$USER --gid=$USER \
            --loglevel=info \
            --pidfile=/tmp/celerybeat.pid
