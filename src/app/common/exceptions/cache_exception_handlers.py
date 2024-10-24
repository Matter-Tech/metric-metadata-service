from copy import deepcopy
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from app.env import SETTINGS


async def save_exception(
    cache_client,
    user_id: UUID,
    internal_id: str,
    ex: Exception,
):
    ex_modified = deepcopy(ex)
    if hasattr(ex_modified, "detail"):
        if ex_modified.detail is not None:
            ex_modified.detail = jsonable_encoder(ex_modified.detail)

    await cache_client.save_object(
        user_id=user_id,
        internal_id=internal_id,
        value=ex,
        object_class=Exception,
        expiration_in_seconds=SETTINGS.cache_error_expiration,
    )


async def find_exception(
    cache_client,
    user_id: UUID,
    internal_id: str,
) -> Exception:
    return (
        await cache_client.find_object(
            user_id=user_id,
            internal_id=internal_id,
            object_class=Exception,
        )
    ).value
