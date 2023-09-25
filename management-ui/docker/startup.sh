#!/usr/bin/bash

env_variable_names=$(compgen -e)
config='{}'

for variable_name in $env_variable_names; do
    if [[ "$variable_name" == VITE__* ]]; then
        config=$(echo "$config" | jq --arg value "${!variable_name}" ".$variable_name = \$value")
    fi
done
echo "$config" > /app/config.json

exec /docker-entrypoint.sh "$@"
