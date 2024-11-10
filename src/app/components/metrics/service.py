import uuid
from typing import List

from matter_exceptions.exceptions.fastapi import ServerError
from matter_observability.metrics import (
    count_occurrence,
    measure_processing_time,
)
from matter_persistence.sql.exceptions import DatabaseError
from matter_persistence.sql.utils import SortMethodModel

from app.components.metrics.dal import MetricDAL
from app.components.metrics.models.metric import MetricModel
from app.components.metrics.models.metric_update import MetricUpdateModel


class MetricService:
    def __init__(
        self,
        dal: MetricDAL,
    ):
        self._dal = dal

    @count_occurrence(label="metrics.get_metric")
    @measure_processing_time(label="metrics.get_metric")
    async def get_metric(
        self,
        metric_id: uuid.UUID,
    ) -> MetricModel:
        return await self._dal.get_metric(metric_id)

    @count_occurrence(label="metrics.find_metrics")
    @measure_processing_time(label="metrics.find_metrics")
    async def find_metrics(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str | None = None,
        sort_method: SortMethodModel | None = None,
        with_deleted: bool = False,
    ) -> List[MetricModel]:
        return await self._dal.find_metrics(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
        )

    @count_occurrence(label="metrics.create_metric")
    @measure_processing_time(label="metrics.create_metric")
    async def create_metric(
        self,
        metric_model: MetricModel,
    ) -> MetricModel:
        try:
            created_metric_model = await self._dal.create_metric(metric_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return created_metric_model

    @count_occurrence(label="metrics.update_metric")
    @measure_processing_time(label="metrics.update_metric")
    async def update_metric(
        self,
        metric_id: uuid.UUID,
        metric_update_model: MetricUpdateModel,
    ) -> MetricModel:
        return await self._dal.update_metric(metric_id, metric_update_model)

    @count_occurrence(label="metrics.delete_metric")
    @measure_processing_time(label="metrics.delete_metric")
    async def delete_metric(
        self,
        metric_id: uuid.UUID,
    ) -> MetricModel:
        return await self._dal.delete_metric(metric_id, soft_delete=True)