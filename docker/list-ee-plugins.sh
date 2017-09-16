#!/bin/sh

find plugins/ -name "*_ee" -type d | while read folder; do
    python_files=$(find $folder -maxdepth 1 -name "*.py")

    if [ -n "$python_files" ]; then
        plugin_name=$(basename $folder | sed 's/^gitmate_//')
        EE_PLUGINS="$plugin_name $EE_PLUGINS"
        echo -n "$plugin_name "
    fi
done

echo
