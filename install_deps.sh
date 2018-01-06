#!/bin/sh
set -e -x

echo "Processing requirements for plugins ..."

for plugin in $(find ./plugins -maxdepth 1 -type d); do
    echo "Checking requirements for $plugin ..."

    requirement="$plugin/requirements.txt"
    install_script="$plugin/gitmate.install.sh"

    if [ -f "$requirement" ]; then
        echo "Found pip requirements.txt on $requirement!"
        pip install --no-cache-dir -r "$requirement"
    fi

    if [ -x "$install_script" ]; then
        echo "Found install script on $install_script!"
        . "$install_script"
    fi
done
