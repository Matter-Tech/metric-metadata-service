from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse

from app.authorization.organization import get_organization_id
from app.dependencies import Dependencies
from app.env import SETTINGS

from .dtos import (
    BaseHelloWorldItemOutDTO,
    ExtendedHelloWorldItemInDTO,
    ExtendedHelloWorldItemOutDTO,
)
from .models import HelloWorldItemRequestModel
from .service import ItemService

item_router = APIRouter(tags=["Items"], prefix=f"{SETTINGS.path_prefix}/v1/items")


@item_router.post(
    "/hello",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseHelloWorldItemOutDTO,
    response_class=JSONResponse,
)
async def post_hello(
    hello_world_item_in_dto: ExtendedHelloWorldItemInDTO,
    item_service: ItemService = Depends(Dependencies.item_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Submit a Hello World Request
    """
    hello_world_item_request_model = HelloWorldItemRequestModel.parse_obj(hello_world_item_in_dto)
    hello_world_item_response_model = await item_service.process_request(hello_world_item_request_model)
    response_dto = BaseHelloWorldItemOutDTO.parse_obj(hello_world_item_response_model)

    return response_dto


@item_router.get(
    "/hello/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ExtendedHelloWorldItemOutDTO,
    response_class=JSONResponse,
)
async def get_hello(
    item_id: Annotated[UUID, Path(title="The ID of the item to get")],
    item_service: ItemService = Depends(Dependencies.item_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Get a Hello World Response
    """
    hello_world_item_response_model = await item_service.get_response(item_id)
    response_dto = ExtendedHelloWorldItemOutDTO.parse_obj(hello_world_item_response_model)
    return response_dto


@item_router.get(
    "/hello",
    status_code=status.HTTP_200_OK,
    response_model=ExtendedHelloWorldItemOutDTO,
    response_class=JSONResponse,
)
async def get_hello_with_query_param(
    item_id: UUID,
    item_service: ItemService = Depends(Dependencies.item_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Get a Hello World Response
    """
    return await get_hello(item_id, item_service, organization_id)
