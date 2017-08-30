#!/usr/bin/env bash

EE_FOLDERS=$(find plugins/ -name "*_ee" -type d)

EE_PLUGINS=""

for folder in $EE_FOLDERS; do
    python_files=(`find $folder -maxdepth 1 -name "*.py"`)

    if [ ${#python_files[@]} -gt 0 ]; then
        plugin_name=$(basename $folder | sed 's/^gitmate_//')
        EE_PLUGINS="$plugin_name $EE_PLUGINS"
    fi
done

echo $EE_PLUGINS
