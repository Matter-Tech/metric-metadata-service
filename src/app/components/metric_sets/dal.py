from datetime import datetime, timezone
from typing import List
from uuid import UUID

from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import get, SortMethodModel, find, commit
from sqlalchemy import select

from app.components.metric_sets.models.metric_set import MetricSetModel
from app.components.metric_sets.models.metric_set_update import MetricSetUpdateModel


class MetricSetDAL:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self._database_manager = database_manager

    async def get_metric_set(
            self,
            metric_set_id: UUID,
    ) -> MetricSetModel:
        statement = select(MetricSetModel).where(MetricSetModel.id == metric_set_id)

        async with self._database_manager.session() as session:
            metric_set_model = await get(
                session=session,
                statement=statement,
            )

            if metric_set_model is None:
                raise DatabaseRecordNotFoundError(
                    description=f"MetricSetModel with Metric Set Id '{metric_set_id}' not found.",
                    detail={
                        "metric_set_id": metric_set_id,
                    },
                )

            return metric_set_model


    async def find_metric_sets(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str = None,
        sort_method: SortMethodModel = None,
        with_deleted: bool = True,
        filters: dict | None = None,
    ) -> List[MetricSetModel]:
        async with self._database_manager.session() as session:
            return await find(
                session=session,
                db_model=MetricSetModel,
                skip=skip,
                limit=limit,
                sort_field=sort_field,
                sort_method=sort_method,
                with_deleted=with_deleted,
                filters=filters,
            )

    async def create_metric_set(self, metric_set_model: MetricSetModel) -> MetricSetModel:
        async with self._database_manager.session() as session:
            session.add(metric_set_model)
            await commit(session)

        return metric_set_model

    async def update_metric_set(
        self,
        metric_set_id: UUID,
        metric_set_update_model: MetricSetUpdateModel,
    ) -> MetricSetModel:
        metric_set_model = await self.get_metric_set(metric_set_id)

        async with self._database_manager.session() as session:
            metric_set_model = await session.merge(metric_set_model)
            for k, v in metric_set_update_model.model_dump().items():
                if k not in [
                    "created",
                    "deleted",
                    "updated",
                ]:
                    if hasattr(metric_set_model, k) and v is not None:
                        setattr(metric_set_model, k, v)

            await commit(session)

        return metric_set_model

    async def delete_metric_set(
        self,
        metric_set_id: UUID,
        soft_delete: bool = True,
    ) -> MetricSetModel:
        metric_set_model = await self.get_metric_set(metric_set_id)

        async with self._database_manager.session() as session:
            metric_set_model = await session.merge(metric_set_model)
            if soft_delete:
                metric_set_model.deleted = datetime.now(tz=timezone.utc)
            else:
                await session.delete(metric_set_model)

            await commit(session)

            if metric_set_model.deleted is None:
                metric_set_model.deleted = datetime.now(tz=timezone.utc)

        return metric_set_model