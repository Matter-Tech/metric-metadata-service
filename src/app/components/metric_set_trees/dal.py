from datetime import datetime, timezone
from typing import List
from uuid import UUID

from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import SortMethodModel, commit, find, get
from sqlalchemy import select

from app.components.metric_set_trees.models.metric_set_tree import MetricSetTreeModel
from app.components.metric_set_trees.models.metric_set_trees_update import MetricSetTreeUpdateModel


class MetricSetTreeDAL:
    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self._database_manager = database_manager

    async def get_metric_set_tree(
        self,
        metric_set_tree_id: UUID,
    ) -> MetricSetTreeModel:
        statement = select(MetricSetTreeModel).where(MetricSetTreeModel.id == metric_set_tree_id)

        async with self._database_manager.session() as session:
            metric_set_tree_model = await get(
                session=session,
                statement=statement,
            )

            if metric_set_tree_model is None:
                raise DatabaseRecordNotFoundError(
                    description=f"MetricSetTreeModel with MetricSetTree Id '{metric_set_tree_id}' not found.",
                    detail={
                        "metric_set_tree_id": metric_set_tree_id,
                    },
                )

            return metric_set_tree_model

    async def find_metric_set_trees(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str = None,
        sort_method: SortMethodModel = None,
        with_deleted: bool = True,
        filters: dict | None = None,
    ) -> List[MetricSetTreeModel]:
        async with self._database_manager.session() as session:
            return await find(
                session=session,
                db_model=MetricSetTreeModel,
                skip=skip,
                limit=limit,
                sort_field=sort_field,
                sort_method=sort_method,
                with_deleted=with_deleted,
                filters=filters,
            )

    async def create_metric_set_tree(self, metric_set_tree_model: MetricSetTreeModel) -> MetricSetTreeModel:
        async with self._database_manager.session() as session:
            session.add(metric_set_tree_model)
            await commit(session)

        return metric_set_tree_model

    async def update_metric_set_tree(
        self,
        metric_set_tree_id: UUID,
        metric_set_tree_update_model: MetricSetTreeUpdateModel,
    ) -> MetricSetTreeModel:
        metric_set_tree_model = await self.get_metric_set_tree(metric_set_tree_id)

        async with self._database_manager.session() as session:
            metric_set_tree_model = await session.merge(metric_set_tree_model)
            for k, v in metric_set_tree_update_model.model_dump().items():
                if k not in [
                    "created",
                    "deleted",
                    "updated",
                ]:  # updated & created are handled by sqlalchemy; deleted is handled by user
                    if hasattr(metric_set_tree_model, k) and v is not None:
                        setattr(metric_set_tree_model, k, v)

            await commit(session)

        return metric_set_tree_model

    async def delete_metric_set_tree(
        self,
        metric_set_tree_id: UUID,
        soft_delete: bool = True,
    ) -> MetricSetTreeModel:
        metric_set_tree_model = await self.get_metric_set_tree(metric_set_tree_id)

        async with self._database_manager.session() as session:
            metric_set_tree_model = await session.merge(metric_set_tree_model)
            if soft_delete:
                metric_set_tree_model.deleted = datetime.now(tz=timezone.utc)
            else:
                await session.delete(metric_set_tree_model)

            await commit(session)

            if metric_set_tree_model.deleted is None:
                metric_set_tree_model.deleted = datetime.now(tz=timezone.utc)

        return metric_set_tree_model
