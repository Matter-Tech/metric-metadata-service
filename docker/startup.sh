#!/bin/bash

set -e

./await_migrations.sh

poetry run python -m app.main
