import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from matter_persistence.sql.utils import SortMethodModel
from pydantic_core import from_json

from app.auth import jwt_authorizer
from app.auth.models import AuthorizedClient
from app.common.enums.enums import EntityTypeEnum, EventTypeEnum
from app.components.events.models.event import EventModel
from app.components.events.service import EventService
from app.components.metric_sets.dtos import (
    FullMetricSetOutDTO,
    MetricSetDeletionOutDTO,
    MetricSetInDTO,
    MetricSetListOutDTO,
    MetricSetOutDTO,
    MetricSetUpdateInDTO,
)
from app.components.metric_sets.models.metric_set import MetricSetModel
from app.components.metric_sets.models.metric_set_update import MetricSetUpdateModel
from app.components.metric_sets.service import MetricSetService
from app.dependencies import Dependencies
from app.env import SETTINGS

metric_set_router = APIRouter(tags=["MetricSets"], prefix=f"{SETTINGS.path_prefix}/v1/metric_sets")
authorizer = jwt_authorizer


@metric_set_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MetricSetOutDTO,
    response_class=JSONResponse,
)
async def create_metric_set(
    metric_set_in_dto: MetricSetInDTO,
    metric_set_service: MetricSetService = Depends(Dependencies.metric_set_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Creates a new metric_set with the provided information.
    """
    metric_set_model = MetricSetModel.parse_obj(metric_set_in_dto)
    created_metric_set_model = await metric_set_service.create_metric_set(
        metric_set_model=metric_set_model,
    )
    response_dto = MetricSetOutDTO.parse_obj(created_metric_set_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.CREATED,
            entity_type=EntityTypeEnum.METRIC_SET,
            node_id=created_metric_set_model.id,
            user_id=client.user_id,
            new_data=from_json(metric_set_in_dto.model_dump_json()),
        )
    )

    return response_dto


@metric_set_router.get(
    "/{target_metric_set_id}",
    status_code=status.HTTP_200_OK,
    response_model=FullMetricSetOutDTO,
    response_class=JSONResponse,
)
async def get_metric_set(
    target_metric_set_id: Annotated[uuid.UUID, Path(title="The ID of the metric_set to retrieve")],
    metric_set_service: MetricSetService = Depends(Dependencies.metric_set_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Fetches the details of a metric_set.
    """
    metric_set_model = await metric_set_service.get_metric_set(metric_set_id=target_metric_set_id)
    response_dto = FullMetricSetOutDTO.parse_obj(metric_set_model)

    return response_dto


@metric_set_router.put(
    "/{target_metric_set_id}",
    status_code=status.HTTP_200_OK,
    response_model=MetricSetOutDTO,
    response_class=JSONResponse,
)
async def update_metric_set(
    target_metric_set_id: Annotated[uuid.UUID, Path(title="The ID of the metric_set to update")],
    metric_set_in_dto: MetricSetUpdateInDTO,
    metric_set_service: MetricSetService = Depends(Dependencies.metric_set_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Update the metric_set's details with the specified data.
    """
    metric_set_update_model = MetricSetUpdateModel.model_validate(metric_set_in_dto.model_dump(exclude_none=True))
    updated_metric_set_model = await metric_set_service.update_metric_set(
        metric_set_id=target_metric_set_id,
        metric_set_update_model=metric_set_update_model,
    )
    response_dto = MetricSetOutDTO.parse_obj(updated_metric_set_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.UPDATED,
            entity_type=EntityTypeEnum.METRIC_SET,
            node_id=updated_metric_set_model.id,
            user_id=client.user_id,
            new_data=from_json(metric_set_in_dto.model_dump_json(exclude_none=True)),
        )
    )

    return response_dto


@metric_set_router.delete(
    "/{target_metric_set_id}",
    status_code=status.HTTP_200_OK,
    response_model=MetricSetDeletionOutDTO,
    response_class=JSONResponse,
)
async def delete_metric_set(
    target_metric_set_id: Annotated[uuid.UUID, Path(title="The ID of the metric_set to delete")],
    metric_set_service: MetricSetService = Depends(Dependencies.metric_set_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Deletes a metric_set with the given target_metric_set_id.
    """
    deleted_metric_set_model = await metric_set_service.delete_metric_set(metric_set_id=target_metric_set_id)
    response_dto = MetricSetDeletionOutDTO.parse_obj(deleted_metric_set_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.DELETED,
            entity_type=EntityTypeEnum.METRIC_SET,
            node_id=target_metric_set_id,
            user_id=client.user_id,
        )
    )

    return response_dto


@metric_set_router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=MetricSetListOutDTO,
    response_class=JSONResponse,
)
async def find_metric_sets(
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
    filters: MetricSetUpdateInDTO | None = Body(None, description="Field to filter"),
    with_deleted: bool | None = Query(False, description="Include deleted metric_sets"),
    metric_set_service: MetricSetService = Depends(Dependencies.metric_set_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Return a list of metric_sets, based on given parameters.
    """
    if filters:
        filters = filters.model_dump(exclude_none=True)
    metric_sets = await metric_set_service.find_metric_sets(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
        filters=filters,
    )
    response_dto = MetricSetListOutDTO(
        count=len(metric_sets),
        metric_sets=FullMetricSetOutDTO.parse_obj(metric_sets),
    )

    return response_dto
