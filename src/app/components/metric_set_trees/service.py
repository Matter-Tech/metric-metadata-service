import asyncio
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
from app.components.utils.meta_data_service import MetaDataService


class MetricSetTreeService:
    def __init__(self, dal: MetricSetTreeDAL, meta_data_service: MetaDataService):
        self._dal = dal
        self._meta_data_service = meta_data_service

    @count_occurrence(label="metric_set_trees.get_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.get_metric_set_tree")
    async def get_metric_set_tree(
            self,
            metric_set_tree_id: uuid.UUID,
    ) -> MetricSetTreeModel:
        metric_set_tree = await self._dal.get_metric_set_tree(metric_set_tree_id=metric_set_tree_id)
        return await self._convert_metadata_out(metric_set_tree=metric_set_tree)

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
        metric_set_trees = await self._dal.find_metric_set_trees(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )
        return await asyncio.gather(*[
            self._convert_metadata_out(metric_set_tree=metric_set_tree) for metric_set_tree in metric_set_trees
        ])

    @count_occurrence(label="metric_set_trees.create_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.create_metric_set_tree")
    async def create_metric_set_tree(
            self,
            metric_set_tree_model: MetricSetTreeModel,
    ) -> MetricSetTreeModel:
        try:
            metric_set_tree_model.meta_data = await self._convert_metadata_names_to_ids(
                meta_data=metric_set_tree_model.meta_data)

            created_metric_set_tree_model = await self._dal.create_metric_set_tree(
                metric_set_tree_model=metric_set_tree_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(metric_set_tree=created_metric_set_tree_model)

    @count_occurrence(label="metric_set_trees.update_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.update_metric_set_tree")
    async def update_metric_set_tree(
            self,
            metric_set_tree_id: uuid.UUID,
            metric_set_tree_update_model: MetricSetTreeUpdateModel,
    ) -> MetricSetTreeModel:
        try:
            metric_set_tree_update_model.meta_data = await self._convert_metadata_names_to_ids(
                meta_data=metric_set_tree_update_model.meta_data)

            updated_metric_set_tree = await self._dal.update_metric_set_tree(metric_set_tree_id=metric_set_tree_id,
                                                                       metric_set_tree_update_model=metric_set_tree_update_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(metric_set_tree=updated_metric_set_tree)

    @count_occurrence(label="metric_set_trees.delete_metric_set_tree")
    @measure_processing_time(label="metric_set_trees.delete_metric_set_tree")
    async def delete_metric_set_tree(
            self,
            metric_set_tree_id: uuid.UUID,
    ) -> MetricSetTreeModel:
        try:
            deleted_metric_set_tree = await self._dal.delete_metric_set_tree(metric_set_tree_id=metric_set_tree_id,
                                                                       soft_delete=True)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(metric_set_tree=deleted_metric_set_tree)

    async def _convert_metadata_out(self, metric_set_tree: MetricSetTreeModel) -> MetricSetTreeModel:
        metric_set_tree.meta_data = await self._convert_metadata_ids_to_names(meta_data=metric_set_tree.meta_data)
        return metric_set_tree

    async def _convert_metadata_ids_to_names(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_ids_to_names(
            entity_type=EntityTypeEnum.METRIC_SET_TREE, meta_data=meta_data
        )

    async def _convert_metadata_names_to_ids(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_names_to_ids(
            entity_type=EntityTypeEnum.METRIC_SET_TREE, meta_data=meta_data
        )
