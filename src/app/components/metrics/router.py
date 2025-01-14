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
from app.components.metrics.dtos import (
    FullMetricOutDTO,
    MetricDeletionOutDTO,
    MetricInDTO,
    MetricListOutDTO,
    MetricOutDTO,
    MetricUpdateInDTO,
)
from app.components.metrics.models.metric import MetricModel
from app.components.metrics.models.metric_update import MetricUpdateModel
from app.components.metrics.service import MetricService
from app.dependencies import Dependencies
from app.env import SETTINGS

metric_router = APIRouter(tags=["Metrics"], prefix=f"{SETTINGS.path_prefix}/v1/metrics")
authorizer = jwt_authorizer


@metric_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MetricOutDTO,
    response_class=JSONResponse,
)
async def create_metric(
    metric_in_dto: MetricInDTO,
    metric_service: MetricService = Depends(Dependencies.metric_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Creates a new metric with the provided information.
    """
    metric_model = MetricModel.parse_obj(metric_in_dto)
    created_metric_model = await metric_service.create_metric(
        metric_model=metric_model,
    )
    response_dto = MetricOutDTO.parse_obj(created_metric_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.CREATED,
            entity_type=EntityTypeEnum.METRIC,
            node_id=created_metric_model.id,
            user_id=client.user_id,
            new_data=from_json(metric_in_dto.model_dump_json()),
        )
    )

    return response_dto


@metric_router.get(
    "/{target_metric_id}",
    status_code=status.HTTP_200_OK,
    response_model=FullMetricOutDTO,
    response_class=JSONResponse,
)
async def get_metric(
    target_metric_id: Annotated[uuid.UUID, Path(title="The ID of the metric to retrieve")],
    metric_service: MetricService = Depends(Dependencies.metric_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Fetches the details of a metric.
    """
    metric_model = await metric_service.get_metric(metric_id=target_metric_id)
    response_dto = FullMetricOutDTO.parse_obj(metric_model)

    return response_dto


@metric_router.put(
    "/{target_metric_id}",
    status_code=status.HTTP_200_OK,
    response_model=MetricOutDTO,
    response_class=JSONResponse,
)
async def update_metric(
    target_metric_id: Annotated[uuid.UUID, Path(title="The ID of the metric to update")],
    metric_in_dto: MetricUpdateInDTO,
    metric_service: MetricService = Depends(Dependencies.metric_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Update the metric's details with the specified data.
    """
    metric_update_model = MetricUpdateModel.model_validate(metric_in_dto.model_dump(exclude_none=True))
    updated_metric_model = await metric_service.update_metric(
        metric_id=target_metric_id,
        metric_update_model=metric_update_model,
    )
    response_dto = MetricOutDTO.parse_obj(updated_metric_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.UPDATED,
            entity_type=EntityTypeEnum.METRIC,
            node_id=updated_metric_model.id,
            user_id=client.user_id,
            new_data=from_json(metric_in_dto.model_dump_json(exclude_none=True)),
        )
    )

    return response_dto


@metric_router.delete(
    "/{target_metric_id}",
    status_code=status.HTTP_200_OK,
    response_model=MetricDeletionOutDTO,
    response_class=JSONResponse,
)
async def delete_metric(
    target_metric_id: Annotated[uuid.UUID, Path(title="The ID of the metric to delete")],
    metric_service: MetricService = Depends(Dependencies.metric_service),
    event_service: EventService = Depends(Dependencies.event_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Deletes a metric with the given target_metric_id.
    """
    deleted_metric_model = await metric_service.delete_metric(metric_id=target_metric_id)
    response_dto = MetricDeletionOutDTO.parse_obj(deleted_metric_model)

    await event_service.create_event(
        EventModel(
            event_type=EventTypeEnum.DELETED,
            entity_type=EntityTypeEnum.METRIC,
            node_id=target_metric_id,
            user_id=client.user_id,
        )
    )

    return response_dto


@metric_router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=MetricListOutDTO,
    response_class=JSONResponse,
)
async def find_metrics(
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
    filters: MetricUpdateInDTO | None = Body(None, description="Field to filter"),
    with_deleted: bool | None = Query(False, description="Include deleted metrics"),
    metric_service: MetricService = Depends(Dependencies.metric_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Return a list of metrics, based on given parameters.
    """
    if filters:
        filters = filters.model_dump(exclude_none=True)
    metrics = await metric_service.find_metrics(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
        filters=filters,
    )
    response_dto = MetricListOutDTO(
        count=len(metrics),
        metrics=FullMetricOutDTO.parse_obj(metrics),
    )

    return response_dto
