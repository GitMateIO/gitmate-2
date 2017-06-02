#!/bin/sh

if [ ! -e "/var/run/docker.sock" ]; then
    echo "Please mount the Docker socket to /var/run/docker.sock"
    exit 1
fi

echo "Sleeping for 10s, just in case the database server isn't ready..."
sleep 10

# Get the host's docker group id
echo "Getting the Docker socket group owner ... "
export docker_group_id=$(stat -c "%g" /var/run/docker.sock)

# Create the docker group in this container
echo "Creating docker group with gid $docker_group_id ..."
groupadd -fr -g $docker_group_id docker

# Add the daemon user to the docker group
echo "Adding $USER to the docker group ..."
usermod -aG $docker_group_id $USER

echo "Collecting static files ..."
python3 manage.py collectstatic --noinput

echo "Migrating database ..."
python3 manage.py migrate

echo "Migrating plugins ..."
python3 manage.py upmate

# For debugging: python3 manage.py runserver 0.0.0.0:8000
exec gunicorn gitmate.wsgi \
    --name=gitmate \
    --workers=$NUM_WORKERS \
    --user=$USER --group=$USER \
    --bind=0.0.0.0:8000 \
    --log-level=$LOG_LEVEL \
    --log-file=-
