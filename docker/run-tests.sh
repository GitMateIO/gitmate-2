#!/bin/sh

set -e -x

. ./docker/common.sh

pip3 install -r test-requirements.txt

if [ -z "$EE_PLUGINS" ]; then
    py.test -vv --cov --doctest-modules
else
    py.test -vv --doctest-modules
fi
