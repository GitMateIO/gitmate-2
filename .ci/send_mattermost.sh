#!/bin/sh

exec curl -X POST \
          -H 'Content-Type: application/json' \
          -d "{ \"text\": \"$2\" }" \
          "$1"
