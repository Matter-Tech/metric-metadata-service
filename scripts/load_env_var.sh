#!/bin/bash

echo "Setting env variables..."

ROOT=$(readlink -f "$(dirname "$0")/..")

if [ ! -f "$ROOT/env/development.env" ]; then
  echo "[ERROR] Environment file not found: $ROOT/env/development.env"
  exit 1
fi

export PYTHONPATH="$ROOT:$ROOT/src"

echo "Loading environment file $ROOT/env/development.env..."
export $(echo $(cat "$ROOT/env/development.env" | sed 's/#.*//g'| xargs) | envsubst)

echo "Done setting env variables."
