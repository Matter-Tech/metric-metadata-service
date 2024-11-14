import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from matter_exceptions.exceptions.fastapi import BaseFastAPIException
from matter_exceptions.exceptions.general import DetailedException
from matter_observability.fastapi import add_middleware
from matter_observability.fastapi.request_id import process_request_id
from matter_observability.logging import LOGGING_CONFIG
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from starlette.middleware.cors import CORSMiddleware

from app.common.exceptions.api_exception_handlers import (
    detailed_exception_handler,
    general_exception_handler,
)
from app.components.data_metrics.router import data_metric_router
from app.components.events.router import event_router
from app.components.health.router import health_router
from app.components.metric_set_trees.router import metric_set_tree_router
from app.components.metric_sets.router import metric_set_router
from app.components.metrics.router import metric_router
from app.components.properties.router import property_router
from app.dependencies import Dependencies
from app.env import SETTINGS


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
    app.include_router(property_router)
    app.include_router(metric_set_router)
    app.include_router(metric_set_tree_router)
    app.include_router(data_metric_router)
    app.include_router(metric_router)
    app.include_router(event_router)

    @app.get("/", response_class=PlainTextResponse)
    async def get_root():
        return "Matter - Metric Metadata Service"

    return app
