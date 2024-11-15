from datetime import datetime, timezone
from typing import List
from uuid import UUID

from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import SortMethodModel, commit, find, get
from sqlalchemy import select

from app.components.properties.models.property import PropertyModel
from app.components.properties.models.property_update import PropertyUpdateModel


class PropertyDAL:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self._database_manager = database_manager

    async def get_property(
        self,
        property_id: UUID,
    ) -> PropertyModel:
        statement = select(PropertyModel).where(PropertyModel.id == property_id)

        async with self._database_manager.session() as session:
            property_model = await get(
                session=session,
                statement=statement,
            )

            if property_model is None:
                raise DatabaseRecordNotFoundError(
                    description=f"PropertyModel with Property Id '{property_id}' not found.",
                    detail={
                        "property_id": property_id,
                    },
                )

            return property_model

    async def find_properties(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str = None,
        sort_method: SortMethodModel = None,
        with_deleted: bool = True,
        filters: dict | None = None,
    ) -> List[PropertyModel]:
        async with self._database_manager.session() as session:
            return await find(
                session=session,
                db_model=PropertyModel,
                skip=skip,
                limit=limit,
                sort_field=sort_field,
                sort_method=sort_method,
                with_deleted=with_deleted,
                filters=filters,
            )

    async def create_property(self, property_model: PropertyModel) -> PropertyModel:
        async with self._database_manager.session() as session:
            session.add(property_model)
            await commit(session)

        return property_model

    async def update_property(
        self,
        property_id: UUID,
        property_update_model: PropertyUpdateModel,
    ) -> PropertyModel:
        property_model = await self.get_property(property_id)

        async with self._database_manager.session() as session:
            property_model = await session.merge(property_model)
            for k, v in property_update_model.model_dump().items():
                if k not in [
                    "created",
                    "deleted",
                    "updated",
                ]:  # updated & created are handled by sqlalchemy; deleted is handled by user
                    if hasattr(property_model, k) and v is not None:
                        setattr(property_model, k, v)

            await commit(session)

        return property_model

    async def delete_property(
        self,
        property_id: UUID,
        soft_delete: bool = True,
    ) -> PropertyModel:
        property_model = await self.get_property(property_id)

        async with self._database_manager.session() as session:
            property_model = await session.merge(property_model)
            if soft_delete:
                property_model.deleted = datetime.now(tz=timezone.utc)
            else:
                await session.delete(property_model)

            await commit(session)

            if property_model.deleted is None:
                property_model.deleted = datetime.now(tz=timezone.utc)

        return property_model
