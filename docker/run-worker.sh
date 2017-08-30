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
addgroup -S -g $docker_group_id host_docker

# Add the daemon user to the docker group
# The host_docker group might not be created if there's already a group with
# the id. In that case we just grep for the existing name, this should always
# work.
echo "Adding $USER to the $(cat /etc/group | grep $docker_group_id | sed 's/:.*//') group ..."
addgroup $USER $(cat /etc/group | grep $docker_group_id | sed 's/:.*//')

exec celery worker \
            -A gitmate \
	    --uid=$USER --gid=$USER \
	    --loglevel=info
