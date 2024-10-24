#!/bin/bash

set -e

poetry run alembic upgrade head
poetry run alembic check

poetry run python -m app.cli create-organization --organization_email admin@website.com --organization_name Apple --first_name Template --last_name Admin
poetry run python -m app.cli create-organization --organization_email manager@website.com --organization_name Amazon --first_name Template --last_name Manager
poetry run python -m app.cli create-organization --organization_email api@website.com --organization_name Tesla --first_name Template --last_name API
poetry run python -m app.cli create-organization --organization_email app@website.com --organization_name SpaceX --first_name Template --last_name App
poetry run python -m app.cli create-organization --organization_email user@website.com --organization_name Microsoft --first_name Template --last_name User
