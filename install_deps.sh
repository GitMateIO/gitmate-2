#!/bin/sh
set -e -x

# install EE plugins
git submodule foreach "
    # install python dependencies, if any
    if [ -f 'requirements.txt' ]; then
        echo 'Found pip requirements...'
        pip install --no-cache-dir -r requirements.txt
    fi

    # run initial setup script, if any
    if [ -x 'gitmate.install.sh' ]; then
        echo 'Running initial script...'
        ./gitmate.install.sh
    fi
"
