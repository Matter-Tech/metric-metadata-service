#!/bin/bash

set -e

IMAGE_REVISION_HEAD=$(poetry run alembic heads --verbose | grep "Revision ID:" | cut -c18-)
IMAGE_REVISION_HISTORY=$(poetry run alembic history --verbose | grep "Revision ID:" | cut -c18-)

echo "Checking if the database is compatible with the image migration revision..."
echo "Image Revision Head: $IMAGE_REVISION_HEAD"
printf "Image Revision History: \n$IMAGE_REVISION_HISTORY\n"

TIMEOUT_SECONDS=30
START_TIME="$(date -u +%s)"
DATABASE_REVISION_CURRENT=""
while true; do
  ALEMBIC_OUTPUT=$(poetry run alembic current --verbose || true)

  if echo "$ALEMBIC_OUTPUT" | grep -q "Revision ID:"; then
    DATABASE_REVISION_CURRENT=$(echo $ALEMBIC_OUTPUT | grep -oP "Revision ID: \K\S+")
  fi

  if echo "$ALEMBIC_OUTPUT" | grep -q "Can't locate revision identified by"; then
    DATABASE_REVISION_CURRENT=$(echo $ALEMBIC_OUTPUT | grep -oP "(?<=(identified by '))[^']*")
  fi

  echo "Current Database Revision: $DATABASE_REVISION_CURRENT"

  CURRENT_TIME="$(date -u +%s)"
  ELAPSED_SECONDS=$(($CURRENT_TIME-$START_TIME))
  if [ $ELAPSED_SECONDS -gt $TIMEOUT_SECONDS ]; then
    echo "timeout of $TIMEOUT_SECONDS sec"
    exit 1
  fi

  if [[ ! "$IMAGE_REVISION_HISTORY" == *"$DATABASE_REVISION_CURRENT"* ]]; then
    # If the current database revision is not in our image history, that means we are running an old image,
    # and we should be compatible with the latest revision in the database.
    echo "The current database revision is not in our history, so we are good to go."
    exit 0
  fi

  if [[ "$IMAGE_REVISION_HEAD" == "$DATABASE_REVISION_CURRENT" ]]; then
    # If the current database revision is our head, that means we are running the latest image,
    # and our database migration job has completed successfully.
    echo "The current database revision is our head, so we are good to go."
    exit 0
  fi

  echo "The current database revision is in our history, but it is not our head."
  echo "We need to wait for the migration job to complete..."
  echo "Elapsed time: $ELAPSED_SECONDS seconds. Timeout is $TIMEOUT_SECONDS seconds."
  echo "Waiting for 5 seconds before checking again..."
  sleep 5
done
