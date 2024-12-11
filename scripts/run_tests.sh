#!/bin/bash

ROOT=$(readlink -f "$(dirname "$0")/..")

COMPOSE_FILE="$ROOT/docker/docker-compose.yaml"

############# Utility methods #############
info() {
  printf "[run_tests.sh] %s\n" "$1"
}

function setup_environment() {
  export PYTHONPATH="$ROOT:$ROOT/src"
  info "Setting PYTHONPATH to $PYTHONPATH"

  DOCKER_DESKTOP_SOCKET="$HOME/.docker/desktop/docker.sock"
  if [ -S $DOCKER_DESKTOP_SOCKET ]; then
      export DOCKER_HOST="unix://$DOCKER_DESKTOP_SOCKET"
      info "Setting DOCKER_HOST to $DOCKER_HOST"
  fi
}

function check_failure_and_exit() {
  for arg; do
    if [ "$arg" -ne 0 ]; then
      info "Tests failed"
      exit "$arg"
    fi
  done
  info "Tests ran successfully!"
}

function start_components_background() {
  info "Starting e2e testing environment..."

  docker-compose -f "$COMPOSE_FILE" down --remove-orphans

  info "Building base image..."
  docker-compose -f "$COMPOSE_FILE" build base-builder --quiet

  info "Building all images..."
  docker-compose -f "$COMPOSE_FILE" build --quiet

  info "Starting containers..."
  docker-compose -f "$COMPOSE_FILE" up --detach

  info "Waiting for the application to start..."
  attempts=0

  until (curl --output /dev/null --silent --fail http://localhost:8080/health) || ((attempts > 60))
  do
    ((attempts++))
    printf '.'
    sleep 1
  done

  if ((attempts > 60))
  then
    printf "\n"
    info "The application failed to start in the e2e testing environment. Tests were not run."
    docker-compose logs
    info "Shutting down e2e testing environment..."
    docker-compose down
    check_failure_and_exit 1
  fi

  # If one or more containers exited with code 1
  if [ $(docker-compose -f "$COMPOSE_FILE" ps | grep -c "Exit 1") -ge 1 ];
  then
    printf "\n"
    info "Some containers exited with errors. Please look at logs."
    info "Shutting down e2e testing environment..."
    docker-compose down
    check_failure_and_exit 1
  fi

  info "E2e testing environment ready..."
}
############# Utility methods - end #############

## Run tests
setup_environment

# Unit tests
python -m pytest --asyncio-mode=auto --capture=tee-sys "$ROOT/tests/unit"
exit_code_unit=$?

# Integration tests
python -m pytest --asyncio-mode=auto --capture=tee-sys "$ROOT/tests/integration"
exit_code_integration=$?

# e2e tests
start_components_background
python -m pytest --capture=tee-sys "$ROOT/tests/e2e/"
exit_code_e2e=$?

if [ "$exit_code_integration" -ne 0 ] || [ "$exit_code_e2e" -ne 0 ]; then
  docker-compose -f "$COMPOSE_FILE" logs
fi

info "Shutting down e2e testing environment..."
docker-compose -f "$COMPOSE_FILE" down

check_failure_and_exit $exit_code_unit $exit_code_integration $exit_code_e2e
