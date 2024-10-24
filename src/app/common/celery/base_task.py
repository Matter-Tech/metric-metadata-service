import logging

from matter_exceptions.detailed_exception import DetailedException
from matter_task_queue import BaseTask, async_to_sync
from sentry_sdk import capture_exception

from app.common.exceptions.cache_exception_handlers import save_exception
from app.env import SETTINGS


class BaseAPITask(BaseTask):
    """

    BaseAPITask Class

    This class extends the BaseTask class and provides additional functionality for handling API related tasks.

    Methods:
    - on_failure(exc, task_id, args, kwargs, einfo): Overrides the on_failure method from the BaseTask class. This method handles any failures that occur during task execution. It logs the
    * error message, captures the exception if SENTRY_DSN is configured, and saves the exception details to the cache if the exception is of type DetailedException and contains a dictionary
    * of organization_id and external_id.

    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)

        description = "Error Detected on Celery Worker: "
        if hasattr(exc, "description"):
            description += exc.description
        else:
            description += str(exc)
        logging.error(description)

        if not SETTINGS.is_env_local_or_test and SETTINGS.sentry_dsn:
            capture_exception(exc)
        if isinstance(exc, DetailedException) and isinstance(exc.detail, dict):
            from app.dependencies import Dependencies

            cache_manager = Dependencies.cache_manager()
            async_to_sync(
                save_exception,
                cache_client=cache_manager,
                organization_id=exc.detail["organization_id"],
                external_id=exc.detail["external_id"],
                ex=exc,
            )
