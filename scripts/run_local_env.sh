#!/bin/bash

ROOT=$(readlink -f "$(dirname "$0")/..")

COMPOSE_FILE="$ROOT/docker/docker-compose.yaml"

echo "Run local environment..."

docker compose -f "$COMPOSE_FILE" down

docker compose -f "$COMPOSE_FILE" build base-builder

docker compose -f "$COMPOSE_FILE" up --build \
  postgres postgres-migration redis auth aws \
  metric-metadata-service-worker-high \
  metric-metadata-service-worker-low \
  metric-metadata-service-celery-beat

docker compose -f "$COMPOSE_FILE" down

echo "Local environment terminated."
