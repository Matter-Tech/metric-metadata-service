import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import JSONResponse
from matter_persistence.sql.utils import SortMethodModel

from app.components.metrics.dtos import MetricOutDTO, FullMetricOutDTO, MetricInDTO, MetricUpdateInDTO, \
    MetricListOutDTO, MetricDeletionOutDTO
from app.components.metrics.models.metric import MetricModel
from app.components.metrics.models.metric_update import MetricUpdateModel
from app.components.metrics.service import MetricService
from app.dependencies import Dependencies
from app.env import SETTINGS


metric_router = APIRouter(tags=["Metrics"], prefix=f"{SETTINGS.path_prefix}/v1/metrics")


@metric_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MetricOutDTO,
    response_class=JSONResponse,
)
async def create_metric(
    metric_in_dto: MetricInDTO,
    metric_service: MetricService = Depends(Dependencies.metric_service),
):
    """
    Creates a new metric with the provided information.
    """
    metric_model = MetricModel.parse_obj(metric_in_dto)
    created_metric_model = await metric_service.create_metric(
        metric_model=metric_model,
    )
    response_dto = MetricOutDTO.parse_obj(created_metric_model)

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
):
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
):
    """
    Update the metric's details with the specified data.
    """
    metric_update_model = MetricUpdateModel.model_validate(metric_in_dto.model_dump(exclude_none=True))
    updated_metric_model = await metric_service.update_metric(
        metric_id=target_metric_id,
        metric_update_model=metric_update_model,
    )
    response_dto = MetricOutDTO.parse_obj(updated_metric_model)

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
):
    """
    Deletes a metric with the given target_metric_id.
    """
    deleted_metric_model = await metric_service.delete_metric(metric_id=target_metric_id)
    response_dto = MetricDeletionOutDTO.parse_obj(deleted_metric_model)

    return response_dto


@metric_router.get(
    "/",
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
    with_deleted: bool | None = Query(False, description="Include deleted metrics"),
    metric_service: MetricService = Depends(Dependencies.metric_service),
):
    """
    Return a list of metrics, based on given parameters.
    """
    metrics = await metric_service.find_metrics(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
    )
    response_dto = MetricListOutDTO(
        count=len(metrics),
        metrics=FullMetricOutDTO.parse_obj(metrics),
    )

    return response_dto
