#!/bin/bash

set -e -x

DEPLOY_SCRIPT=".ci/deploy.master.sh"

which ssh-agent || (apt-get update -y && apt-get install -y --no-install-recommends openssh-client)
eval $(ssh-agent -s)
ssh-add <(echo "$DEPLOY_PRIVATE_KEY")
mkdir -p ~/.ssh
echo "$DEPLOY_SERVER_HOSTKEYS" > ~/.ssh/known_hosts

if [ "$DEPLOY_RELEASE" -eq "YES" ]; then
    DEPLOY_SCRIPT=".ci/deploy.release.sh"
fi

ssh tomoko@moon.gitmate.io 'bash -s' < .ci/deploy.master.sh
