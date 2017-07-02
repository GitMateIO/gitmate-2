#!/bin/sh

command="celery beat -A gitmate"
command="$command --loglevel=info"
command="$command --pidfile=/tmp/celerybeat.pid"

export command

exec su - $USER \
        -s /bin/bash \
        --preserve-environment \
        -c "$command"
