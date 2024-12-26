#!/bin/bash

set -e

./init_database.sh

./await_migrations.sh

poetry run python -m app.main
