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
from app.components.utils.validation_service import ValidationService


class MetricSetService:
    def __init__(self, dal: MetricSetDAL, validation_service: ValidationService):
        self._dal = dal
        self._validation_service = validation_service

    @count_occurrence(label="metric_sets.get_metric_set")
    @measure_processing_time(label="metric_sets.get_metric_set")
    async def get_metric_set(
        self,
        metric_set_id: uuid.UUID,
    ) -> MetricSetModel:
        return await self._dal.get_metric_set(metric_set_id)

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
        return await self._dal.find_metric_sets(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
            filters=filters,
        )

    @count_occurrence(label="metric_sets.create_metric_set")
    @measure_processing_time(label="metric_sets.create_metric_set")
    async def create_metric_set(
        self,
        metric_set_model: MetricSetModel,
    ) -> MetricSetModel:
        try:
            await self._validation_service.validate_metadata(
                entity_type=EntityTypeEnum.METRIC_SET, meta_data=metric_set_model.meta_data
            )

            created_metric_set_model = await self._dal.create_metric_set(metric_set_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return created_metric_set_model

    @count_occurrence(label="metric_sets.update_metric_set")
    @measure_processing_time(label="metric_sets.update_metric_set")
    async def update_metric_set(
        self,
        metric_set_id: uuid.UUID,
        metric_set_update_model: MetricSetUpdateModel,
    ) -> MetricSetModel:
        await self._validation_service.validate_metadata(
            entity_type=EntityTypeEnum.METRIC_SET, meta_data=metric_set_update_model.meta_data
        )

        return await self._dal.update_metric_set(metric_set_id, metric_set_update_model)

    @count_occurrence(label="metric_sets.delete_metric_set")
    @measure_processing_time(label="metric_sets.delete_metric_set")
    async def delete_metric_set(
        self,
        metric_set_id: uuid.UUID,
    ) -> MetricSetModel:
        return await self._dal.delete_metric_set(metric_set_id, soft_delete=True)
