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
from app.components.metric_sets.dal import MetricSetDAL
from app.components.metric_sets.models.metric_set import MetricSetModel
from app.components.metric_sets.models.metric_set_update import MetricSetUpdateModel
from app.components.utils.meta_data_service import MetaDataService


class MetricSetService:
    def __init__(self, dal: MetricSetDAL, meta_data_service: MetaDataService):
        self._dal = dal
        self._meta_data_service = meta_data_service

    @count_occurrence(label="metric_sets.get_metric_set")
    @measure_processing_time(label="metric_sets.get_metric_set")
    async def get_metric_set(
        self,
        metric_set_id: uuid.UUID,
    ) -> MetricSetModel:
        metric_set = await self._dal.get_metric_set(metric_set_id=metric_set_id)
        return await self._convert_metadata_out(metric_set=metric_set)

    @count_occurrence(label="metric_sets.find_metric_sets")
    @measure_processing_time(label="metric_sets.find_metric_sets")
    async def find_metric_sets(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str | None = None,
        sort_method: SortMethodModel | None = None,
        with_deleted: bool = False,
        filters: dict | None = None,
    ) -> List[MetricSetModel]:
        metric_sets = await self._dal.find_metric_sets(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )

        return await asyncio.gather(*[
            self._convert_metadata_out(metric_set=metric_set) for metric_set in metric_sets
        ])

    @count_occurrence(label="metric_sets.create_metric_set")
    @measure_processing_time(label="metric_sets.create_metric_set")
    async def create_metric_set(
        self,
        metric_set_model: MetricSetModel,
    ) -> MetricSetModel:
        try:
            metric_set_model.meta_data = await self._convert_metadata_names_to_ids(meta_data=metric_set_model.meta_data)

            created_metric_set_model = await self._dal.create_metric_set(metric_set_model=metric_set_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(metric_set=created_metric_set_model)

    @count_occurrence(label="metric_sets.update_metric_set")
    @measure_processing_time(label="metric_sets.update_metric_set")
    async def update_metric_set(
        self,
        metric_set_id: uuid.UUID,
        metric_set_update_model: MetricSetUpdateModel,
    ) -> MetricSetModel:
        try:
            metric_set_update_model.meta_data = await self._convert_metadata_names_to_ids(
            meta_data=metric_set_update_model.meta_data)

            updated_metric_set = await self._dal.update_metric_set(metric_set_id=metric_set_id, metric_set_update_model=metric_set_update_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(metric_set=updated_metric_set)

    @count_occurrence(label="metric_sets.delete_metric_set")
    @measure_processing_time(label="metric_sets.delete_metric_set")
    async def delete_metric_set(
        self,
        metric_set_id: uuid.UUID,
    ) -> MetricSetModel:
        try:
            deleted_metric_set = await self._dal.delete_metric_set(metric_set_id=metric_set_id, soft_delete=True)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(metric_set=deleted_metric_set)

    async def _convert_metadata_out(self, metric_set: MetricSetModel) -> MetricSetModel:
        metric_set.meta_data = await self._convert_metadata_ids_to_names(meta_data=metric_set.meta_data)
        return metric_set

    async def _convert_metadata_ids_to_names(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_ids_to_names(
            entity_type=EntityTypeEnum.METRIC_SET, meta_data=meta_data
        )

    async def _convert_metadata_names_to_ids(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_names_to_ids(
            entity_type=EntityTypeEnum.METRIC_SET, meta_data=meta_data
        )
