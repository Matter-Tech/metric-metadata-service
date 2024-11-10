from datetime import datetime, timezone
from typing import List
from uuid import UUID

from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import get, SortMethodModel, find, commit
from sqlalchemy import select

from app.components.metrics.models.metric import MetricModel
from app.components.metrics.models.metric_update import MetricUpdateModel


class MetricDAL:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self._database_manager = database_manager

    async def get_metric(
            self,
            metric_id: UUID,
    ) -> MetricModel:
        statement = select(MetricModel).where(MetricModel.id == metric_id)

        async with self._database_manager.session() as session:
            metric_model = await get(
                session=session,
                statement=statement,
            )

            if metric_model is None:
                raise DatabaseRecordNotFoundError(
                    description=f"MetricModel with Metric Set Id '{metric_id}' not found.",
                    detail={
                        "metric_id": metric_id,
                    },
                )

            return metric_model


    async def find_metrics(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str = None,
        sort_method: SortMethodModel = None,
        with_deleted: bool = True,
        filters: dict | None = None,
    ) -> List[MetricModel]:
        async with self._database_manager.session() as session:
            return await find(
                session=session,
                db_model=MetricModel,
                skip=skip,
                limit=limit,
                sort_field=sort_field,
                sort_method=sort_method,
                with_deleted=with_deleted,
                filters=filters,
            )

    async def create_metric(self, metric_model: MetricModel) -> MetricModel:
        async with self._database_manager.session() as session:
            session.add(metric_model)
            await commit(session)

        return metric_model

    async def update_metric(
        self,
        metric_id: UUID,
        metric_update_model: MetricUpdateModel,
    ) -> MetricModel:
        metric_model = await self.get_metric(metric_id)

        async with self._database_manager.session() as session:
            metric_model = await session.merge(metric_model)
            for k, v in metric_update_model.model_dump().items():
                if k not in [
                    "created",
                    "deleted",
                    "updated",
                ]:
                    if hasattr(metric_model, k) and v is not None:
                        setattr(metric_model, k, v)

            await commit(session)

        return metric_model

    async def delete_metric(
        self,
        metric_id: UUID,
        soft_delete: bool = True,
    ) -> MetricModel:
        metric_model = await self.get_metric(metric_id)

        async with self._database_manager.session() as session:
            metric_model = await session.merge(metric_model)
            if soft_delete:
                metric_model.deleted = datetime.now(tz=timezone.utc)
            else:
                await session.delete(metric_model)

            await commit(session)

            if metric_model.deleted is None:
                metric_model.deleted = datetime.now(tz=timezone.utc)

        return metric_model