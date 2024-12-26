FROM python:3.12-slim

ARG PROJECT_NAME=metric-metadata-service
ARG PROJECT_PATH_IN_DOCKER=/opt/${PROJECT_NAME}

RUN apt-get update && apt-get upgrade -y \
    && apt-get install build-essential libcurl4-openssl-dev libssl-dev python3-dev -y \
    && apt-get clean  \
    && pip install --upgrade pip

RUN useradd --uid 10000 runner \
    && chown 10000:10000 /opt

ENV PYTHONBUFFERED = 1

# Configure Poetry
ENV POETRY_VERSION=1.8.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION} \
    && mkdir ${POETRY_CACHE_DIR} \
    && chown 10000:10000 ${POETRY_CACHE_DIR}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

USER 10000

# Install dependencies
WORKDIR ${PROJECT_PATH_IN_DOCKER}
COPY ../poetry.lock pyproject.toml README.md ./
COPY ../scripts/await_migrations.sh await_migrations.sh
COPY ../docker/startup.sh startup.sh
COPY src/app ./app
COPY src/alembic ./alembic
COPY src/alembic.ini alembic.ini

RUN poetry install --only main

COPY ../scripts/init_database.sh init_database.sh

EXPOSE 8080

CMD [ "bash", "-c", "./startup.sh" ]
