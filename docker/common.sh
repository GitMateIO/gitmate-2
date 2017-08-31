#!/bin/sh

export EE_PLUGINS=$(./docker/list-ee-plugins.sh)

echo "EE plugins found: $EE_PLUGINS"
