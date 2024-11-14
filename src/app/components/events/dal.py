from datetime import datetime, timezone
from typing import List
from uuid import UUID

from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import SortMethodModel, commit, find, get
from sqlalchemy import select

from app.components.events.models.event import EventModel


class EventDAL:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self._database_manager = database_manager

    async def get_event(
        self,
        event_id: UUID,
    ) -> EventModel:
        statement = select(EventModel).where(EventModel.id == event_id)

        async with self._database_manager.session() as session:
            event_model = await get(
                session=session,
                statement=statement,
            )

            if event_model is None:
                raise DatabaseRecordNotFoundError(
                    description=f"EventModel with Event Id '{event_id}' not found.",
                    detail={
                        "event_id": event_id,
                    },
                )

            return event_model

    async def find_events(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str = None,
        sort_method: SortMethodModel = None,
        with_deleted: bool = True,
        filters: dict | None = None,
    ) -> List[EventModel]:
        async with self._database_manager.session() as session:
            return await find(
                session=session,
                db_model=EventModel,
                skip=skip,
                limit=limit,
                sort_field=sort_field,
                sort_method=sort_method,
                with_deleted=with_deleted,
                filters=filters,
            )

    async def create_event(self, event_model: EventModel) -> EventModel:
        async with self._database_manager.session() as session:
            session.add(event_model)
            await commit(session)

        return event_model

    async def delete_event(
        self,
        event_id: UUID,
        soft_delete: bool = True,
    ) -> EventModel:
        event_model = await self.get_event(event_id)

        async with self._database_manager.session() as session:
            event_model = await session.merge(event_model)
            if soft_delete:
                event_model.deleted = datetime.now(tz=timezone.utc)
            else:
                await session.delete(event_model)

            await commit(session)

            if event_model.deleted is None:
                event_model.deleted = datetime.now(tz=timezone.utc)

        return event_model
