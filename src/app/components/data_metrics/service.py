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
from app.components.data_metrics.dal import DataMetricDAL
from app.components.data_metrics.models.data_metric import DataMetricModel
from app.components.data_metrics.models.data_metric_update import DataMetricUpdateModel
from app.components.utils.meta_data_service import MetaDataService


class DataMetricService:
    def __init__(self, dal: DataMetricDAL, meta_data_service: MetaDataService):
        self._dal = dal
        self._meta_data_service = meta_data_service

    @count_occurrence(label="data_metrics.get_data_metric")
    @measure_processing_time(label="data_metrics.get_data_metric")
    async def get_data_metric(
        self,
        data_metric_id: uuid.UUID,
    ) -> DataMetricModel:
        data_metric = await self._dal.get_data_metric(data_metric_id=data_metric_id)
        return await self._convert_metadata_out(data_metric=data_metric)

    @count_occurrence(label="data_metrics.find_data_metrics")
    @measure_processing_time(label="data_metrics.find_data_metrics")
    async def find_data_metrics(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str | None = None,
        sort_method: SortMethodModel | None = None,
        with_deleted: bool = False,
        filters: dict | None = None,
    ) -> List[DataMetricModel]:
        data_metrics = await self._dal.find_data_metrics(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )

        return await asyncio.gather(
            *[self._convert_metadata_out(data_metric=data_metric) for data_metric in data_metrics]
        )

    @count_occurrence(label="data_metrics.create_data_metric")
    @measure_processing_time(label="data_metrics.create_data_metric")
    async def create_data_metric(
        self,
        data_metric_model: DataMetricModel,
    ) -> DataMetricModel:
        try:
            data_metric_model.meta_data = await self._convert_metadata_names_to_ids(
                meta_data=data_metric_model.meta_data
            )
            created_data_metric_model = await self._dal.create_data_metric(data_metric_model=data_metric_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(data_metric=created_data_metric_model)

    @count_occurrence(label="data_metrics.update_data_metric")
    @measure_processing_time(label="data_metrics.update_data_metric")
    async def update_data_metric(
        self,
        data_metric_id: uuid.UUID,
        data_metric_update_model: DataMetricUpdateModel,
    ) -> DataMetricModel:
        try:
            data_metric_update_model.meta_data = await self._convert_metadata_names_to_ids(
                meta_data=data_metric_update_model.meta_data
            )
            updated_data_metric = await self._dal.update_data_metric(
                data_metric_id=data_metric_id, data_metric_update_model=data_metric_update_model
            )
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(data_metric=updated_data_metric)

    @count_occurrence(label="data_metrics.delete_data_metric")
    @measure_processing_time(label="data_metrics.delete_data_metric")
    async def delete_data_metric(
        self,
        data_metric_id: uuid.UUID,
    ) -> DataMetricModel:
        try:
            deleted_data_metric = await self._dal.delete_data_metric(data_metric_id=data_metric_id, soft_delete=True)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return await self._convert_metadata_out(data_metric=deleted_data_metric)

    async def _convert_metadata_out(self, data_metric: DataMetricModel) -> DataMetricModel:
        data_metric.meta_data = await self._convert_metadata_ids_to_names(meta_data=data_metric.meta_data)
        return data_metric

    async def _convert_metadata_ids_to_names(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_ids_to_names(
            entity_type=EntityTypeEnum.DATA_METRIC, meta_data=meta_data
        )

    async def _convert_metadata_names_to_ids(self, meta_data: dict) -> dict:
        if meta_data is None:
            return {}
        return await self._meta_data_service.convert_metadata_names_to_ids(
            entity_type=EntityTypeEnum.DATA_METRIC, meta_data=meta_data
        )
