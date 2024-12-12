#!/bin/bash

ROOT=$(readlink -f "$(dirname "$0")/..")

COMPOSE_FILE="$ROOT/docker/docker-compose.yaml"

echo "Run local environment..."

docker compose -f "$COMPOSE_FILE" down
docker compose -f "$COMPOSE_FILE" build base-builder
docker compose -f "$COMPOSE_FILE" up --build
docker compose -f "$COMPOSE_FILE" down

echo "Local environment terminated."
