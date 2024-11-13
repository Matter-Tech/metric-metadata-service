import uuid
from typing import List

from matter_exceptions.exceptions.fastapi import ServerError
from matter_observability.metrics import (
    count_occurrence,
    measure_processing_time,
)
from matter_persistence.sql.exceptions import DatabaseError
from matter_persistence.sql.utils import SortMethodModel

from app.common.enums.enums import EntityTypeEnum
from app.components.metric_set_trees.dal import MetricSetTreeDAL
from app.components.metric_set_trees.models.metric_set_tree import MetricSetTreeModel
from app.components.metric_set_trees.models.metric_set_trees_update import MetricSetTreeUpdateModel
from app.components.utils.validation_service import ValidationService


class MetricSetTreeService:
    def __init__(self, dal: MetricSetTreeDAL, validation_service: ValidationService):
        self._dal = dal
        self._validation_service = validation_service

    @count_occurrence(label="metric_set_trees.get_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.get_metric_set_tree")
    async def get_metric_set_tree(
        self,
        metric_set_tree_id: uuid.UUID,
    ) -> MetricSetTreeModel:
        return await self._dal.get_metric_set_tree(metric_set_tree_id)

    @count_occurrence(label="metric_set_trees.find_metric_set_trees")
    @measure_processing_time(label="metric_set_trees.find_metric_set_trees")
    async def find_metric_set_trees(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str | None = None,
        sort_method: SortMethodModel | None = None,
        with_deleted: bool = False,
        filters: dict | None = None,
    ) -> List[MetricSetTreeModel]:
        return await self._dal.find_metric_set_trees(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )

    @count_occurrence(label="metric_set_trees.create_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.create_metric_set_tree")
    async def create_metric_set_tree(
        self,
        metric_set_tree_model: MetricSetTreeModel,
    ) -> MetricSetTreeModel:
        try:
            await self._validation_service.validate_metadata(
                entity_type=EntityTypeEnum.METRIC_SET_TREE, meta_data=metric_set_tree_model.meta_data
            )

            created_metric_set_tree_model = await self._dal.create_metric_set_tree(metric_set_tree_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return created_metric_set_tree_model

    @count_occurrence(label="metric_set_trees.update_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.update_metric_set_tree")
    async def update_metric_set_tree(
        self,
        metric_set_tree_id: uuid.UUID,
        metric_set_tree_update_model: MetricSetTreeUpdateModel,
    ) -> MetricSetTreeModel:
        await self._validation_service.validate_metadata(
            entity_type=EntityTypeEnum.METRIC_SET_TREE, meta_data=metric_set_tree_update_model.meta_data
        )

        return await self._dal.update_metric_set_tree(metric_set_tree_id, metric_set_tree_update_model)

    @count_occurrence(label="metric_set_trees.delete_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.delete_metric_set_tree")
    async def delete_metric_set_tree(
        self,
        metric_set_tree_id: uuid.UUID,
    ) -> MetricSetTreeModel:
        return await self._dal.delete_metric_set_tree(metric_set_tree_id, soft_delete=True)
