#!/usr/bin/env bash

case $1 in
    master)
        IMAGE_NAME=$MASTER_NAME
        DEPLOY_SCRIPT=".ci/deploy.master.sh"
        ;;
    release)
        IMAGE_NAME=$RELEASE_NAME
        DEPLOY_SCRIPT=".ci/deploy.release.sh"
        ;;
    *)
        echo "Usage: $0 {master|release}"
        exit 1
esac

set -e -x -o pipefail

docker login -e gitlab-ci@gitlab.com -u gitlab-ci-token -p $CI_JOB_TOKEN registry.gitlab.com
docker pull $TEST_IMAGE_NAME
docker tag $TEST_IMAGE_NAME $RELEASE_NAME
docker push $RELEASE_NAME
which ssh-agent || (apk update && apk add openssh)
eval $(ssh-agent -s)
ssh-add <(echo "$DEPLOY_PRIVATE_KEY")
mkdir -p ~/.ssh
echo "$DEPLOY_SERVER_HOSTKEYS" > ~/.ssh/known_hosts
ssh tomoko@moon.gitmate.io 'bash -s' < "$DEPLOY_SCRIPT"
