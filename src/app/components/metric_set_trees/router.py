import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from matter_persistence.sql.utils import SortMethodModel

from app.auth import jwt_authorizer
from app.auth.models import AuthorizedClient
from app.components.metric_set_trees.dtos import (
    FullMetricSetTreeOutDTO,
    MetricSetTreeDeletionOutDTO,
    MetricSetTreeInDTO,
    MetricSetTreeListOutDTO,
    MetricSetTreeOutDTO,
    MetricSetTreeUpdateInDTO,
)
from app.components.metric_set_trees.models.metric_set_tree import MetricSetTreeModel
from app.components.metric_set_trees.models.metric_set_trees_update import MetricSetTreeUpdateModel
from app.components.metric_set_trees.service import MetricSetTreeService
from app.dependencies import Dependencies
from app.env import SETTINGS

metric_set_tree_router = APIRouter(tags=["MetricSetTrees"], prefix=f"{SETTINGS.path_prefix}/v1/metric_set_trees")
authorizer = jwt_authorizer


@metric_set_tree_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MetricSetTreeOutDTO,
    response_class=JSONResponse,
)
async def create_metric_set_tree(
    metric_set_tree_in_dto: MetricSetTreeInDTO,
    metric_set_tree_service: MetricSetTreeService = Depends(Dependencies.metric_set_tree_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Creates a new metric_set_tree with the provided information.
    """
    metric_set_tree_model = MetricSetTreeModel.parse_obj(metric_set_tree_in_dto)
    created_metric_set_tree_model = await metric_set_tree_service.create_metric_set_tree(
        metric_set_tree_model=metric_set_tree_model,
    )
    response_dto = MetricSetTreeOutDTO.parse_obj(created_metric_set_tree_model)

    return response_dto


@metric_set_tree_router.get(
    "/{target_metric_set_tree_id}",
    status_code=status.HTTP_200_OK,
    response_model=FullMetricSetTreeOutDTO,
    response_class=JSONResponse,
)
async def get_metric_set_tree(
    target_metric_set_tree_id: Annotated[uuid.UUID, Path(title="The ID of the metric_set_tree to retrieve")],
    metric_set_tree_service: MetricSetTreeService = Depends(Dependencies.metric_set_tree_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Fetches the details of a metric_set_tree.
    """
    metric_set_tree_model = await metric_set_tree_service.get_metric_set_tree(
        metric_set_tree_id=target_metric_set_tree_id
    )
    response_dto = FullMetricSetTreeOutDTO.parse_obj(metric_set_tree_model)

    return response_dto


@metric_set_tree_router.put(
    "/{target_metric_set_tree_id}",
    status_code=status.HTTP_200_OK,
    response_model=MetricSetTreeOutDTO,
    response_class=JSONResponse,
)
async def update_metric_set_tree(
    target_metric_set_tree_id: Annotated[uuid.UUID, Path(title="The ID of the metric_set_tree to update")],
    metric_set_tree_in_dto: MetricSetTreeUpdateInDTO,
    metric_set_tree_service: MetricSetTreeService = Depends(Dependencies.metric_set_tree_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Update the metric_set_tree's details with the specified data.
    """
    metric_set_tree_update_model = MetricSetTreeUpdateModel.model_validate(
        metric_set_tree_in_dto.model_dump(exclude_none=True)
    )
    updated_metric_set_tree_model = await metric_set_tree_service.update_metric_set_tree(
        metric_set_tree_id=target_metric_set_tree_id,
        metric_set_tree_update_model=metric_set_tree_update_model,
    )
    response_dto = MetricSetTreeOutDTO.parse_obj(updated_metric_set_tree_model)

    return response_dto


@metric_set_tree_router.delete(
    "/{target_metric_set_tree_id}",
    status_code=status.HTTP_200_OK,
    response_model=MetricSetTreeDeletionOutDTO,
    response_class=JSONResponse,
)
async def delete_metric_set_tree(
    target_metric_set_tree_id: Annotated[uuid.UUID, Path(title="The ID of the metric_set_tree to delete")],
    metric_set_tree_service: MetricSetTreeService = Depends(Dependencies.metric_set_tree_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Deletes a metric_set_tree with the given target_metric_set_tree_id.
    """
    deleted_metric_set_tree_model = await metric_set_tree_service.delete_metric_set_tree(
        metric_set_tree_id=target_metric_set_tree_id
    )
    response_dto = MetricSetTreeDeletionOutDTO.parse_obj(deleted_metric_set_tree_model)

    return response_dto


@metric_set_tree_router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=MetricSetTreeListOutDTO,
    response_class=JSONResponse,
)
async def find_metric_set_trees(
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
    filters: MetricSetTreeUpdateInDTO | None = Body(None, description="Field to filter"),
    with_deleted: bool | None = Query(False, description="Include deleted metric_set_trees"),
    metric_set_tree_service: MetricSetTreeService = Depends(Dependencies.metric_set_tree_service),
    client: AuthorizedClient = Depends(authorizer),
):
    if not client.is_super_user():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    """
    Return a list of metric_set_trees, based on given parameters.
    """
    if filters:
        filters = filters.model_dump(exclude_none=True)
    metric_set_trees = await metric_set_tree_service.find_metric_set_trees(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
        filters=filters,
    )
    response_dto = MetricSetTreeListOutDTO(
        count=len(metric_set_trees),
        metric_set_trees=FullMetricSetTreeOutDTO.parse_obj(metric_set_trees),
    )

    return response_dto
