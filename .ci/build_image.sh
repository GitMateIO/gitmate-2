#!/usr/bin/env bash
set -x -e -o pipefail

docker build -t $TEST_IMAGE_NAME

docker login -e gitlab-ci@gitlab.com \
       -u gitlab-ci-token -p $CI_JOB_TOKEN \
       registry.gitlab.com

docker push $TEST_IMAGE_NAME
