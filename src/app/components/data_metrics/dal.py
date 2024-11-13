from datetime import datetime, timezone
from typing import List
from uuid import UUID

from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import SortMethodModel, commit, find, get
from sqlalchemy import select

from app.components.data_metrics.models.data_metric import DataMetricModel
from app.components.data_metrics.models.data_metric_update import DataMetricUpdateModel


class DataMetricDAL:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self._database_manager = database_manager

    async def get_data_metric(
        self,
        data_metric_id: UUID,
    ) -> DataMetricModel:
        statement = select(DataMetricModel).where(DataMetricModel.id == data_metric_id)

        async with self._database_manager.session() as session:
            data_metric_model = await get(
                session=session,
                statement=statement,
            )

            if data_metric_model is None:
                raise DatabaseRecordNotFoundError(
                    description=f"DataMetricModel with Metric Set Id '{data_metric_id}' not found.",
                    detail={
                        "data_metric_id": data_metric_id,
                    },
                )

            return data_metric_model

    async def find_data_metrics(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str = None,
        sort_method: SortMethodModel = None,
        with_deleted: bool = True,
        filters: dict | None = None,
    ) -> List[DataMetricModel]:
        async with self._database_manager.session() as session:
            return await find(
                session=session,
                db_model=DataMetricModel,
                skip=skip,
                limit=limit,
                sort_field=sort_field,
                sort_method=sort_method,
                with_deleted=with_deleted,
                filters=filters,
            )

    async def create_data_metric(self, data_metric_model: DataMetricModel) -> DataMetricModel:
        async with self._database_manager.session() as session:
            session.add(data_metric_model)
            await commit(session)

        return data_metric_model

    async def update_data_metric(
        self,
        data_metric_id: UUID,
        data_metric_update_model: DataMetricUpdateModel,
    ) -> DataMetricModel:
        data_metric_model = await self.get_data_metric(data_metric_id)

        async with self._database_manager.session() as session:
            data_metric_model = await session.merge(data_metric_model)
            for k, v in data_metric_update_model.model_dump().items():
                if k not in [
                    "created",
                    "deleted",
                    "updated",
                ]:
                    if hasattr(data_metric_model, k) and v is not None:
                        setattr(data_metric_model, k, v)

            await commit(session)

        return data_metric_model

    async def delete_data_metric(
        self,
        data_metric_id: UUID,
        soft_delete: bool = True,
    ) -> DataMetricModel:
        data_metric_model = await self.get_data_metric(data_metric_id)

        async with self._database_manager.session() as session:
            data_metric_model = await session.merge(data_metric_model)
            if soft_delete:
                data_metric_model.deleted = datetime.now(tz=timezone.utc)
            else:
                await session.delete(data_metric_model)

            await commit(session)

            if data_metric_model.deleted is None:
                data_metric_model.deleted = datetime.now(tz=timezone.utc)

        return data_metric_model
