#!/usr/bin/env bash
set -x -e -o pipefail

docker login -e gitlab-ci@gitlab.com -u gitlab-ci-token -p $CI_JOB_TOKEN registry.gitlab.com
docker pull $TEST_IMAGE_NAME
docker tag $TEST_IMAGE_NAME $IMAGE_NAME
docker push $IMAGE_NAME
