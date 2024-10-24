import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import sentry_sdk
from celery.signals import worker_process_init, worker_process_shutdown
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from matter_exceptions.exceptions.fastapi import BaseFastAPIException
from matter_exceptions.exceptions.general import DetailedException
from matter_observability.fastapi import add_middleware
from matter_observability.fastapi.request_id import process_request_id
from matter_observability.logging import LOGGING_CONFIG
from matter_task_queue import create_celery
from matter_task_queue.utils import async_to_sync
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from starlette.middleware.cors import CORSMiddleware

from app.common.exceptions.api_exception_handlers import (
    detailed_exception_handler,
    general_exception_handler,
)
from app.components.health.router import health_router
from app.components.items.router import item_router
from app.components.organizations.router import organization_router
from app.dependencies import Dependencies
from app.env import SETTINGS

from .cron_jobs import CELERYBEAT_SCHEDULE


def _sentry_tracing_sampler(sampling_context: dict[str, Any]) -> float:
    # always inherit
    if sampling_context.get("parent_sampled") is not None:
        return sampling_context["parent_sampled"]
    # skip health checks & metrics
    elif any(
        path_part in sampling_context.get("asgi_scope", {}).get("path", "") for path_part in ("health", "metrics")
    ):
        return 0.0
    return SETTINGS.default_tracing_sample_rate


@asynccontextmanager
async def _app_lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """
    Governs startup & shutdown of the app, as recommended by FastAPI: https://fastapi.tiangolo.com/advanced/events/

    Args:
        _: the FastAPI app
    """
    logging.info("Initiating dependencies...")
    Dependencies.start()
    logging.info("Done initiating dependencies.")

    yield

    logging.info("Closing connections to DB & cache...")
    await Dependencies.stop()
    logging.info("Done closing connections to DB & cache.")
    logging.info("Application is shutting down...")


@worker_process_init.connect()
def worker_process_init(**kwargs):
    """
    Celery worker process startup.
    """
    logging.info("Worker Process Initialization started...")
    logging.info("Initiating dependencies...")
    from app.dependencies import Dependencies

    Dependencies.start()
    logging.info("Done initiating dependencies.")
    logging.info("Done Worker Process Initialization.")


@worker_process_shutdown.connect()
def worker_process_shutdown(**kwargs):
    """
    Celery worker process shutdown.
    """
    logging.info(f"Worker process [{kwargs['pid']}] shutdown... -> Exit Code: [{kwargs['exitcode']}]")
    logging.info("Closing connections to DB & cache...")
    from app.dependencies import Dependencies

    async_to_sync(Dependencies.stop)
    logging.info("Done closing connections to DB & cache.")
    logging.info("Done worker process shutdown.")


def create_app() -> FastAPI:
    """
    Creates FastAPI app instance.
    Mounts routers, and adds a root endpoint.
    """

    # Setup Sentry
    if SETTINGS.sentry_dsn and not SETTINGS.is_env_local_or_test:
        sentry_sdk.init(
            dsn=SETTINGS.sentry_dsn,
            traces_sampler=_sentry_tracing_sampler,
            integrations=[AsyncioIntegration()],
            environment=SETTINGS.env,
        )

    # Setup Logs
    logging.config.dictConfig(LOGGING_CONFIG)

    # Create API
    app = FastAPI(title="metric-metadata-service", version="1.0.0", lifespan=_app_lifespan)

    # Add Observability
    add_middleware(app=app)

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # type: ignore
        allow_methods=["*"],  # type: ignore
        allow_headers=["*"],  # type: ignore
    )
    app.middleware("http")(process_request_id)

    # Exception Handlers
    app.add_exception_handler(DetailedException, detailed_exception_handler)
    app.add_exception_handler(BaseFastAPIException, general_exception_handler)

    # Apply Routers
    app.include_router(health_router)
    app.include_router(organization_router)
    app.include_router(item_router)

    # Add Celery
    app.celery_app = create_celery(
        task_module_paths=[
            "app.components.items.tasks",
        ],
        celery_beat_schedule=CELERYBEAT_SCHEDULE,
    )

    @app.get("/", response_class=PlainTextResponse)
    async def get_root():
        return "Matter - Metric Metadata Service"

    return app
