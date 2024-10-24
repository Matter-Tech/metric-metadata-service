from uuid import UUID

from matter_persistence.redis.exceptions import CacheRecordNotFoundError, CacheRecordNotSavedError
from matter_persistence.redis.manager import CacheManager

from app.authorization.organization import pass_organization_id
from app.common.exceptions.exceptions import (
    HelloResponseNotFoundError,
    HelloResponseNotSavedError,
)
from app.env import SETTINGS

from .models import HelloWorldItemResponseModel


class ItemDAL:
    """
    ItemDAL class is responsible for accessing and manipulating cache records for items.

    Methods:
    - get_hello_from_cache: Retrieves the hello response record from the cache.
    - save_hello_in_cache: Saves the hello response record in the cache.

    Attributes:
    - _cache_client: An instance of APICacheClient used for interacting with the cache.

    Example Usage:
    ```python
    # Create an instance of ItemDAL
    item_dal = ItemDAL(cache_client)

    # Get hello response from cache
    response = item_dal.get_hello_from_cache(organization_id, item_id)

    # Save hello response in cache
    item_dal.save_hello_in_cache(organization_id, hello_response)
    ```
    """

    def __init__(
        self,
        cache_manager: CacheManager,
    ):
        self._cache_manager = cache_manager

    @pass_organization_id
    async def get_hello_from_cache(
        self,
        organization_id: UUID,
        item_id: UUID,
    ) -> HelloWorldItemResponseModel:
        try:
            hello_response_record = await self._cache_manager.get_value(
                organization_id=organization_id,
                internal_id=item_id,
                object_class=HelloWorldItemResponseModel,
            )
        except CacheRecordNotFoundError as ex:
            raise HelloResponseNotFoundError(
                description=f"Hello Response for id {item_id} is not found",
                detail={
                    "internal_id": item_id,
                    "organization_id": organization_id,
                    "exception": ex,
                },
            )

        return hello_response_record.value

    @pass_organization_id
    async def save_hello_in_cache(
        self,
        organization_id: UUID,
        hello_response: HelloWorldItemResponseModel,
    ):
        try:
            await self._cache_manager.save_value(
                organization_id=organization_id,
                internal_id=hello_response.id,
                value=hello_response,
                object_class=type(hello_response),
                expiration_in_seconds=SETTINGS.cache_default_record_expiration,
            )
        except CacheRecordNotSavedError as ex:
            raise HelloResponseNotSavedError(
                description=f"Hello Response for id {hello_response.id} cannot be saved",
                detail={
                    "response_key": hello_response.id,
                    "organization_id": organization_id,
                    "exception": ex,
                },
            )
