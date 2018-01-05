#!/bin/sh

: ${BEAT_SCHEDULE_FOLDER:="/var/run/gitmate-beat/"}

BEAT_SCHEDULE_FILE="$BEAT_SCHEDULE_FOLDER/schedule"
BEAT_PID_FILE="$BEAT_SCHEDULE_FOLDER/beat.pid"

if [ ! -d "$BEAT_SCHEDULE_FOLDER" ]; then
    mkdir -p $BEAT_SCHEDULE_FOLDER
    chown $USER:$USER $BEAT_SCHEDULE_FOLDER
fi

exec celery beat \
            -A gitmate \
            -s $BEAT_SCHEDULE_FILE \
	    --uid=$USER --gid=$USER \
            --loglevel=info \
            --pidfile=$BEAT_PID_FILE \
            $EXTRA_ARGUMENTS
