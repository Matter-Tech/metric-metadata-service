import logging

from fastapi import Request
from matter_exceptions import DetailedException
from matter_exceptions.exceptions.fastapi import (
    BaseFastAPIException,
    ConflictError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from matter_persistence.sql.exceptions import (
    DatabaseError,
    DatabaseIntegrityError,
    DatabaseInvalidSortFieldError,
    DatabaseRecordNotFoundError,
)
from starlette.responses import JSONResponse

from app.env import SETTINGS


async def detailed_exception_handler(_: Request, exc: DetailedException):
    if isinstance(exc, DatabaseRecordNotFoundError):
        fastapi_exc = NotFoundError(
            description=exc.description,
            detail=exc.detail,
        )

    elif isinstance(exc, DatabaseError):
        fastapi_exc = ServerError(description=exc.description, detail=exc.detail)

    elif isinstance(exc, DatabaseIntegrityError) or isinstance(exc, DatabaseInvalidSortFieldError):
        fastapi_exc = ValidationError(description=exc.description, detail=exc.detail)

    else:
        fastapi_exc = ServerError(description=exc.description, detail=exc.detail)

    return await general_exception_handler(_, fastapi_exc)


async def general_exception_handler(_: Request, exc: BaseFastAPIException):
    """
    This handler covers the following errors:

    UnauthorizedError,
    ServerError,
    ConflictError,
    NotFoundError,
    AccessDeniedError,
    ValidationError,
    UnprocessableError,
    """

    message = f"API Returned an Error: Status Code: {exc.status_code} <---> Description: {exc.description} <---> Details: {exc.detail}"
    if isinstance(exc, ServerError):
        logging.error(message)
    else:
        logging.warning(message)

    if not isinstance(exc, ConflictError):
        if SETTINGS.sentry_dsn and not SETTINGS.is_env_local_or_test:
            from sentry_sdk import capture_exception, set_extra

            set_extra("error", exc)
            set_extra("metadata", exc.detail)
            capture_exception(exc)

    json_data = exc.as_dict()
    if SETTINGS.env == "prod":
        del json_data["detail"]

    return JSONResponse(
        json_data,
        status_code=exc.status_code,
    )
