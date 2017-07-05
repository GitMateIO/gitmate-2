#!/usr/bin/env bash
set -x -e -o pipefail

# GitMate master deployment script
# This script is meant to be executed inside the master server

COMPOSE_LOCATION="/opt/gitmate/master"
DOCKER_GROUP_NAME="docker"

# Early checks

which docker

which docker-compose

id -nG | grep -qw "$DOCKER_GROUP_NAME"

# Start deployment

cd $COMPOSE_LOCATION

docker-compose pull --parallel

docker-compose up -d
