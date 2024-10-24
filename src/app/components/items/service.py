from uuid import UUID

from matter_exceptions.exceptions.fastapi import NotFoundError, ServerError
from matter_observability.metrics import (
    count_occurrence,
    measure_processing_time,
)
from matter_task_queue import run_task_async

from app.common.exceptions.exceptions import (
    HelloResponseNotFoundError,
    HelloResponseNotSavedError,
)

from .dal import ItemDAL
from .models import HelloWorldItemRequestModel, HelloWorldItemResponseModel
from .tasks import hello_world_item_task


class ItemService:
    """
    The `ItemService` class is responsible for processing item requests and retrieving item responses.

    Methods:
    - `process_request`: Process a request to item for hello world.
    - `get_response`: Get the response for a given item ID.

    """

    def __init__(
        self,
        dal: ItemDAL,
    ):
        self._dal = dal

    @count_occurrence(label="items")
    @measure_processing_time(label="items")
    async def process_request(
        self,
        hello_world_item_request_model: HelloWorldItemRequestModel,
    ) -> HelloWorldItemResponseModel:
        """

        Process a request for a hello world item.

        Args:
            hello_world_item_request_model (HelloWorldItemRequestModel): The request model containing the ID of the item.

        Returns:
            HelloWorldItemResponseModel: The response model containing the ID and the generated value.

        Raises:
            ServerError: If the response model cannot be saved in the cache.

        """
        await run_task_async(hello_world_item_task, hello_world_item_request_model.id)

        hello_world_item_response_model = HelloWorldItemResponseModel(
            id=hello_world_item_request_model.id,
            value="My New Generated Value",
        )

        try:
            await self._dal.save_hello_in_cache(hello_world_item_response_model)
        except HelloResponseNotSavedError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return hello_world_item_response_model

    async def get_response(
        self,
        item_id: UUID,
    ) -> HelloWorldItemResponseModel:
        """

        Method: get_response

        Retrieve the response for a given item ID.

        Parameters:
        - self: The current instance of the class.
        - item_id: The unique identifier of the item for which to retrieve the response.

        Returns:
        A HelloWorldItemResponseModel object representing the response for the given item ID.

        Raises:
        - NotFoundError: If no response is found for the given item ID.

        """
        try:
            return await self._dal.get_hello_from_cache(item_id)
        except HelloResponseNotFoundError as ex:
            raise NotFoundError(description=ex.description, detail=ex.detail)
