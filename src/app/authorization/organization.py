import functools
import inspect
from uuid import UUID

from fastapi import Depends
from matter_exceptions.exceptions.fastapi import UnauthorizedError

from app.authorization.context import get_request_organization_id, set_identity

from .jwt import decode_jwt
from .models import IdentityModel


async def get_organization_id(identity: IdentityModel = Depends(decode_jwt)) -> UUID:
    set_identity(identity=identity)
    return identity.organization_id


def pass_organization_id(method):
    @functools.wraps(method)
    async def wrapper_async(self, *args, **kwargs):
        try:
            organization_id = get_request_organization_id()
        except LookupError:
            raise UnauthorizedError(
                description="User Unauthorized: User Identity object not found",
            )
        # Perform any pre-coroutine operations here
        return await method(self, organization_id, *args, **kwargs)

    @functools.wraps(method)
    def wrapper_sync(self, *args, **kwargs):
        try:
            organization_id = get_request_organization_id()
        except LookupError:
            raise UnauthorizedError(
                description="User Unauthorized: User Identity object not found",
            )
        # Perform any pre-coroutine operations here
        return method(self, organization_id, *args, **kwargs)

    if inspect.iscoroutinefunction(method):
        return wrapper_async
    return wrapper_sync
