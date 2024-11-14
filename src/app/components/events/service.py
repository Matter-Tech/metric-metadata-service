import uuid
from typing import List

from matter_exceptions.exceptions.fastapi import ServerError
from matter_observability.metrics import (
    count_occurrence,
    measure_processing_time,
)
from matter_persistence.sql.exceptions import DatabaseError
from matter_persistence.sql.utils import SortMethodModel

from app.components.events.dal import EventDAL
from app.components.events.models.event import EventModel


class EventService:
    def __init__(self, dal: EventDAL):
        self._dal = dal

    @count_occurrence(label="events.get_event")
    @measure_processing_time(label="events.get_event")
    async def get_event(
        self,
        event_id: uuid.UUID,
    ) -> EventModel:
        return await self._dal.get_event(event_id)

    @count_occurrence(label="events.find_events")
    @measure_processing_time(label="events.find_events")
    async def find_events(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str | None = None,
        sort_method: SortMethodModel | None = None,
        with_deleted: bool = False,
        filters: dict | None = None,
    ) -> List[EventModel]:
        return await self._dal.find_events(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )

    @count_occurrence(label="events.create_event")
    @measure_processing_time(label="events.create_event")
    async def create_event(
        self,
        event_model: EventModel,
    ) -> EventModel:
        try:
            created_event_model = await self._dal.create_event(event_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return created_event_model

    @count_occurrence(label="events.delete_event")
    @measure_processing_time(label="events.delete_event")
    async def delete_event(
        self,
        event_id: uuid.UUID,
    ) -> EventModel:
        return await self._dal.delete_event(event_id, soft_delete=True)
