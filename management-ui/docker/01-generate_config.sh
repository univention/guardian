#!/bin/bash

if [ -z ${SKIP_CONFIG_GENERATION+x} ]; then
    env_variable_names=$(compgen -e)
    config='{}'
    config_path="/app/config"

    for variable_name in $env_variable_names; do
        if [[ "$variable_name" == VITE__* ]]; then
            config=$(echo "$config" | jq --arg value "${!variable_name}" ".$variable_name = \$value")
        fi
    done
    mkdir -p "$config_path"
    echo "$config" > "$config_path/config.json"
else
    echo "Skipping generation of config.json"
fi

