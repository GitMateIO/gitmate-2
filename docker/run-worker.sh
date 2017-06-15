#!/bin/sh

if [ ! -e "/var/run/docker.sock" ]; then
    echo "Please mount the Docker socket to /var/run/docker.sock"
    exit 1
fi

# Get the host's docker group id
echo "Getting the Docker socket group owner ... "
export docker_group_id=$(stat -c "%g" /var/run/docker.sock)

# Create the docker group in this container
echo "Creating host_docker group with gid $docker_group_id ..."
groupadd -fr -g $docker_group_id host_docker

# Add the daemon user to the docker group
echo "Adding $USER to the docker group ..."
usermod -aG $docker_group_id $USER

exec python3 manage.py celeryd \
    --uid=$USER --gid=$USER \
    --settings=gitmate.settings \
    --loglevel=$LOG_LEVEL \
    --pool=gevent \
    --concurrency=$NUM_WORKERS
