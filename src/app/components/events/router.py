import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.responses import JSONResponse
from matter_persistence.sql.utils import SortMethodModel

from app.components.events.dtos import (
    EventDeletionOutDTO,
    EventFilterInDTO,
    EventListOutDTO,
    FullEventOutDTO,
)
from app.components.events.service import EventService
from app.dependencies import Dependencies
from app.env import SETTINGS

event_router = APIRouter(tags=["Events"], prefix=f"{SETTINGS.path_prefix}/v1/events")


@event_router.get(
    "/{target_event_id}",
    status_code=status.HTTP_200_OK,
    response_model=FullEventOutDTO,
    response_class=JSONResponse,
)
async def get_event(
    target_event_id: Annotated[uuid.UUID, Path(title="The ID of the event to retrieve")],
    event_service: EventService = Depends(Dependencies.event_service),
):
    """
    Fetches the details of a event.
    """
    event_model = await event_service.get_event(event_id=target_event_id)
    response_dto = FullEventOutDTO.parse_obj(event_model)

    return response_dto


@event_router.delete(
    "/{target_event_id}",
    status_code=status.HTTP_200_OK,
    response_model=EventDeletionOutDTO,
    response_class=JSONResponse,
)
async def delete_event(
    target_event_id: Annotated[uuid.UUID, Path(title="The ID of the event to delete")],
    event_service: EventService = Depends(Dependencies.event_service),
):
    """
    Deletes a event with the given target_event_id.
    """
    deleted_event_model = await event_service.delete_event(event_id=target_event_id)
    response_dto = EventDeletionOutDTO.parse_obj(deleted_event_model)

    return response_dto


@event_router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=EventListOutDTO,
    response_class=JSONResponse,
)
async def find_events(
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
    filters: EventFilterInDTO | None = Body(None, description="Field to filter"),
    with_deleted: bool | None = Query(False, description="Include deleted events"),
    event_service: EventService = Depends(Dependencies.event_service),
):
    """
    Return a list of events, based on given parameters.
    """
    if filters:
        filters = filters.model_dump(exclude_none=True)
    events = await event_service.find_events(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
        filters=filters,
    )
    response_dto = EventListOutDTO(
        count=len(events),
        events=FullEventOutDTO.parse_obj(events),
    )

    return response_dto
