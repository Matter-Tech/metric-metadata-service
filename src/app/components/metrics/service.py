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
from app.components.metrics.dal import MetricDAL
from app.components.metrics.models.metric import MetricModel
from app.components.metrics.models.metric_update import MetricUpdateModel
from app.components.utils.meta_data_service import MetaDataService


class MetricService:
    def __init__(self, dal: MetricDAL, meta_data_service: MetaDataService):
        self._dal = dal
        self._meta_data_service = meta_data_service

    @count_occurrence(label="metrics.get_metric")
    @measure_processing_time(label="metrics.get_metric")
    async def get_metric(
            self,
            metric_id: uuid.UUID,
    ) -> MetricModel:
        metric = await self._dal.get_metric(metric_id=metric_id)
        return await self._convert_metadata_out(metric=metric)

    @count_occurrence(label="metrics.find_metrics")
    @measure_processing_time(label="metrics.find_metrics")
    async def find_metrics(
            self,
            skip: int = 0,
            limit: int = None,
            sort_field: str | None = None,
            sort_method: SortMethodModel | None = None,
            with_deleted: bool = False,
            filters: dict | None = None,
    ) -> List[MetricModel]:
        metrics = await self._dal.find_metrics(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )

        return await asyncio.gather(*[
            self._convert_metadata_out(metric) for metric in metrics
        ])

    @count_occurrence(label="metrics.create_metric")
    @measure_processing_time(label="metrics.create_metric")
    async def create_metric(
            self,
            metric_model: MetricModel,
    ) -> MetricModel:
        try:
            metric_model.meta_data = await self._convert_metadata_names_to_ids(meta_data=metric_model.meta_data)

            created_metric_model = await self._dal.create_metric(metric_model=metric_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(metric=created_metric_model)

    @count_occurrence(label="metrics.update_metric")
    @measure_processing_time(label="metrics.update_metric")
    async def update_metric(
            self,
            metric_id: uuid.UUID,
            metric_update_model: MetricUpdateModel,
    ) -> MetricModel:
        try:
            metric_update_model.meta_data = await self._convert_metadata_names_to_ids(
                meta_data=metric_update_model.meta_data)

            updated_metric = await self._dal.update_metric(metric_id=metric_id, metric_update_model=metric_update_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)
        return await self._convert_metadata_out(metric=updated_metric)

    @count_occurrence(label="metrics.delete_metric")
    @measure_processing_time(label="metrics.delete_metric")
    async def delete_metric(
            self,
            metric_id: uuid.UUID,
    ) -> MetricModel:
        try:
            deleted_metric = await self._dal.delete_metric(metric_id, soft_delete=True)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)
        return await self._convert_metadata_out(metric=deleted_metric)

    async def _convert_metadata_out(self, metric: MetricModel) -> MetricModel:
        metric.meta_data = await self._convert_metadata_ids_to_names(meta_data=metric.meta_data)
        return metric

    async def _convert_metadata_ids_to_names(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_ids_to_names(
            entity_type=EntityTypeEnum.METRIC, meta_data=meta_data
        )

    async def _convert_metadata_names_to_ids(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_names_to_ids(
            entity_type=EntityTypeEnum.METRIC, meta_data=meta_data
        )
