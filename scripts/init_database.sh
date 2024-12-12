#!/bin/bash

set -e

poetry run alembic upgrade head
poetry run alembic check
