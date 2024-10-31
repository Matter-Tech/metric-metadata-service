import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import JSONResponse
from matter_persistence.sql.utils import SortMethodModel

from app.dependencies import Dependencies
from app.env import SETTINGS

from .dtos import (
    FullPropertyOutDTO,
    PropertyDeletionOutDTO,
    PropertyInDTO,
    PropertyOutDTO,
    PropertyUpdateInDTO,
    PropertyListOutDTO,
)
from .models.property import PropertyModel
from .models.property_update import PropertyUpdateModel
from .service import PropertyService

property_router = APIRouter(tags=["Properties"], prefix=f"{SETTINGS.path_prefix}/v1/properties")


@property_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PropertyOutDTO,
    response_class=JSONResponse,
)
async def create_property(
    property_in_dto: PropertyInDTO,
    property_service: PropertyService = Depends(Dependencies.property_service),
):
    """
    Creates a new property with the provided information.
    """
    property_model = PropertyModel.parse_obj(property_in_dto)
    created_property_model = await property_service.create_property(
        property_model=property_model,
    )
    response_dto = PropertyOutDTO.parse_obj(created_property_model)

    return response_dto


@property_router.get(
    "/{target_property_id}",
    status_code=status.HTTP_200_OK,
    response_model=FullPropertyOutDTO,
    response_class=JSONResponse,
)
async def get_property(
    target_property_id: Annotated[uuid.UUID, Path(title="The ID of the property to retrieve")],
    property_service: PropertyService = Depends(Dependencies.property_service),
):
    """
    Fetches the details of a property.
    """
    property_model = await property_service.get_property(property_id=target_property_id)
    response_dto = FullPropertyOutDTO.parse_obj(property_model)

    return response_dto


@property_router.put(
    "/{target_property_id}",
    status_code=status.HTTP_200_OK,
    response_model=PropertyOutDTO,
    response_class=JSONResponse,
)
async def update_property(
    target_property_id: Annotated[uuid.UUID, Path(title="The ID of the property to update")],
    property_in_dto: PropertyUpdateInDTO,
    property_service: PropertyService = Depends(Dependencies.property_service),
):
    """
    Update the property's details with the specified data.
    """
    property_update_model = PropertyUpdateModel.parse_obj(property_in_dto)
    updated_property_model = await property_service.update_property(
        property_id=target_property_id,
        property_update_model=property_update_model,
    )
    response_dto = PropertyOutDTO.parse_obj(updated_property_model)

    return response_dto


@property_router.delete(
    "/{target_property_id}",
    status_code=status.HTTP_200_OK,
    response_model=PropertyDeletionOutDTO,
    response_class=JSONResponse,
)
async def delete_property(
    target_property_id: Annotated[uuid.UUID, Path(title="The ID of the property to delete")],
    property_service: PropertyService = Depends(Dependencies.property_service),
):
    """
    Deletes a property with the given target_property_id.
    """
    deleted_property_model = await property_service.delete_property(property_id=target_property_id)
    response_dto = PropertyDeletionOutDTO.parse_obj(deleted_property_model)

    return response_dto


@property_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=PropertyListOutDTO,
    response_class=JSONResponse,
)
async def find_properties(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(
        SETTINGS.pagination_limit_default,
        ge=0,
        le=SETTINGS.pagination_limit_max,
        description="Number of items to retrieve",
    ),
    sort_field: str = Query(None, title="Sort field", description="Field to sort by"),
    sort_method: SortMethodModel = Query(
        SortMethodModel.ASC, title="Sort method", description="Sort method: asc or desc"
    ),
    with_deleted: bool | None = Query(False, description="Include deleted properties"),
    property_service: PropertyService = Depends(Dependencies.property_service),
):
    """
    Return a list of properties, based on given parameters.
    """
    properties = await property_service.find_properties(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
    )
    response_dto = PropertyListOutDTO(
        count=len(properties),
        properties=FullPropertyOutDTO.parse_obj(properties),
    )

    return response_dto
