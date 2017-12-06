#!/bin/sh
set -x -e -o pipefail

SOURCE="$1"
TARGET="$2"

docker pull $SOURCE || docker build -t $SOURCE .
docker tag $SOURCE $TARGET
docker push $TARGET
