import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from matter_persistence.sql.utils import SortMethodModel
from pydantic_core import from_json

from app.auth import jwt_authorizer
from app.auth.models import AuthorizedClient
from app.common.enums.enums import EntityTypeEnum, EventTypeEnum
from app.components.data_metrics.dtos import (
    DataMetricDeletionOutDTO,
    DataMetricInDTO,
    DataMetricListOutDTO,
    DataMetricOutDTO,
    DataMetricUpdateInDTO,
    FullDataMetricOutDTO,
)
from app.components.data_metrics.models.data_metric import DataMetricModel
from app.components.data_metrics.models.data_metric_update import DataMetricUpdateModel
from app.components.data_metrics.service import DataMetricService
from app.components.events.models.event import EventModel
from app.components.events.service import EventService
from app.dependencies import Dependencies
from app.env import SETTINGS

data_metric_router = APIRouter(tags=["DataMetrics"], prefix=f"{SETTINGS.path_prefix}/v1/data_metrics")
authorizer = jwt_authorizer


@data_metric_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DataMetricOutDTO,
    response_class=JSONResponse,
)
async def create_data_metric(
    data_metric_in_dto: DataMetricInDTO,
    data_metric_service: DataMetricService = Depends(Dependencies.data_metric_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Creates a new data_metric with the provided information.
    """
    data_metric_model = DataMetricModel.parse_obj(data_metric_in_dto)
    created_data_metric_model = await data_metric_service.create_data_metric(
        data_metric_model=data_metric_model,
    )
    response_dto = DataMetricOutDTO.parse_obj(created_data_metric_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.CREATED,
            entity_type=EntityTypeEnum.METRIC,
            node_id=created_data_metric_model.id,
            user_id=client.user_id,
            new_data=from_json(data_metric_in_dto.model_dump_json()),
        )
    )

    return response_dto


@data_metric_router.get(
    "/{target_data_metric_id}",
    status_code=status.HTTP_200_OK,
    response_model=FullDataMetricOutDTO,
    response_class=JSONResponse,
)
async def get_data_metric(
    target_data_metric_id: Annotated[uuid.UUID, Path(title="The ID of the data_metric to retrieve")],
    data_metric_service: DataMetricService = Depends(Dependencies.data_metric_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Fetches the details of a data_metric.
    """
    data_metric_model = await data_metric_service.get_data_metric(data_metric_id=target_data_metric_id)
    response_dto = FullDataMetricOutDTO.parse_obj(data_metric_model)

    return response_dto


@data_metric_router.put(
    "/{target_data_metric_id}",
    status_code=status.HTTP_200_OK,
    response_model=DataMetricOutDTO,
    response_class=JSONResponse,
)
async def update_data_metric(
    target_data_metric_id: Annotated[uuid.UUID, Path(title="The ID of the data_metric to update")],
    data_metric_in_dto: DataMetricUpdateInDTO,
    data_metric_service: DataMetricService = Depends(Dependencies.data_metric_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Update the data_metric's details with the specified data.
    """
    data_metric_update_model = DataMetricUpdateModel.model_validate(data_metric_in_dto.model_dump(exclude_none=True))
    updated_data_metric_model = await data_metric_service.update_data_metric(
        data_metric_id=target_data_metric_id,
        data_metric_update_model=data_metric_update_model,
    )
    response_dto = DataMetricOutDTO.parse_obj(updated_data_metric_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.UPDATED,
            entity_type=EntityTypeEnum.METRIC,
            node_id=updated_data_metric_model.id,
            user_id=client.user_id,
            new_data=from_json(data_metric_in_dto.model_dump_json(exclude_none=True)),
        )
    )

    return response_dto


@data_metric_router.delete(
    "/{target_data_metric_id}",
    status_code=status.HTTP_200_OK,
    response_model=DataMetricDeletionOutDTO,
    response_class=JSONResponse,
)
async def delete_data_metric(
    target_data_metric_id: Annotated[uuid.UUID, Path(title="The ID of the data_metric to delete")],
    data_metric_service: DataMetricService = Depends(Dependencies.data_metric_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Deletes a data_metric with the given target_data_metric_id.
    """
    deleted_data_metric_model = await data_metric_service.delete_data_metric(data_metric_id=target_data_metric_id)
    response_dto = DataMetricDeletionOutDTO.parse_obj(deleted_data_metric_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.DELETED,
            entity_type=EntityTypeEnum.DATA_METRIC,
            node_id=target_data_metric_id,
            user_id=client.user_id,
        )
    )

    return response_dto


@data_metric_router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=DataMetricListOutDTO,
    response_class=JSONResponse,
)
async def filter_data_metrics(
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
    with_deleted: bool | None = Query(False, description="Include deleted data_metrics"),
    filters: DataMetricUpdateInDTO | None = Body(None, description="Field to filter"),
    data_metric_service: DataMetricService = Depends(Dependencies.data_metric_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Return a list of data_metrics, based on given parameters.
    """
    if filters:
        filters = filters.model_dump(exclude_none=True)
    data_metrics = await data_metric_service.find_data_metrics(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
        filters=filters,
    )
    response_dto = DataMetricListOutDTO(
        count=len(data_metrics),
        data_metrics=FullDataMetricOutDTO.parse_obj(data_metrics),
    )

    return response_dto
