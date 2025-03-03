#!/bin/bash

# Usage: ./bin.sh [command]
# Example: ./bin.sh ls -la

# Define the container name
CONTAINER_NAME="web"

# Execute the command in the web container
docker compose exec $CONTAINER_NAME poetry run python llm_translator/manage.py "$@"