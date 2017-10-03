#!/bin/sh -e -x

function install {
    # install python dependencies, if any
    if [ -f 'requirements.txt' ]; then
        echo $"\nFound pip requirements...\n"
        pip install --no-cache-dir -r requirements.txt
    fi

    # run initial setup script, if any
    if [ -x 'gitmate.install.sh' ]; then
        echo $"\nRunning initial script...\n"
        ./gitmate.install.sh
    fi
}
export -f install
git submodule foreach install
