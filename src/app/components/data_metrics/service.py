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
from app.components.utils.validation_service import ValidationService


class DataMetricService:
    def __init__(self, dal: DataMetricDAL, validation_service: ValidationService):
        self._dal = dal
        self._validation_service = validation_service

    @count_occurrence(label="data_metrics.get_data_metric")
    @measure_processing_time(label="data_metrics.get_data_metric")
    async def get_data_metric(
        self,
        data_metric_id: uuid.UUID,
    ) -> DataMetricModel:
        return await self._dal.get_data_metric(data_metric_id)

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
        return await self._dal.find_data_metrics(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )

    @count_occurrence(label="data_metrics.create_data_metric")
    @measure_processing_time(label="data_metrics.create_data_metric")
    async def create_data_metric(
        self,
        data_metric_model: DataMetricModel,
    ) -> DataMetricModel:
        try:
            await self._validation_service.validate_metadata(
                entity_type=EntityTypeEnum.DATA_METRIC, meta_data=data_metric_model.meta_data
            )

            created_data_metric_model = await self._dal.create_data_metric(data_metric_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return created_data_metric_model

    @count_occurrence(label="data_metrics.update_data_metric")
    @measure_processing_time(label="data_metrics.update_data_metric")
    async def update_data_metric(
        self,
        data_metric_id: uuid.UUID,
        data_metric_update_model: DataMetricUpdateModel,
    ) -> DataMetricModel:
        await self._validation_service.validate_metadata(
            entity_type=EntityTypeEnum.DATA_METRIC, meta_data=data_metric_update_model.meta_data
        )

        return await self._dal.update_data_metric(data_metric_id, data_metric_update_model)

    @count_occurrence(label="data_metrics.delete_data_metric")
    @measure_processing_time(label="data_metrics.delete_data_metric")
    async def delete_data_metric(
        self,
        data_metric_id: uuid.UUID,
    ) -> DataMetricModel:
        return await self._dal.delete_data_metric(data_metric_id, soft_delete=True)
