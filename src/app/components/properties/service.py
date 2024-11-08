import uuid
from typing import List

from matter_exceptions.exceptions.fastapi import ServerError
from matter_observability.metrics import (
    count_occurrence,
    measure_processing_time,
)
from matter_persistence.sql.exceptions import DatabaseError
from matter_persistence.sql.utils import SortMethodModel

from app.components.properties.dal import PropertyDAL
from app.components.properties.models.property import PropertyModel
from app.components.properties.models.property_update import PropertyUpdateModel


class PropertyService:
    def __init__(
        self,
        dal: PropertyDAL,
    ):
        self._dal = dal

    @count_occurrence(label="properties.get_property")
    @measure_processing_time(label="properties.get_property")
    async def get_property(
        self,
        property_id: uuid.UUID,
    ) -> PropertyModel:
        return await self._dal.get_property(property_id)

    @count_occurrence(label="properties.find_properties")
    @measure_processing_time(label="properties.find_properties")
    async def find_properties(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str | None = None,
        sort_method: SortMethodModel | None = None,
        with_deleted: bool = False,
    ) -> List[PropertyModel]:
        return await self._dal.find_properties(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
        )

    @count_occurrence(label="properties.create_property")
    @measure_processing_time(label="properties.create_property")
    async def create_property(
        self,
        property_model: PropertyModel,
    ) -> PropertyModel:
        try:
            created_property_model = await self._dal.create_property(property_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return created_property_model

    @count_occurrence(label="properties.update_property")
    @measure_processing_time(label="properties.update_property")
    async def update_property(
        self,
        property_id: uuid.UUID,
        property_update_model: PropertyUpdateModel,
    ) -> PropertyModel:
        return await self._dal.update_property(property_id, property_update_model)

    @count_occurrence(label="properties.delete_property")
    @measure_processing_time(label="properties.delete_property")
    async def delete_property(
        self,
        property_id: uuid.UUID,
    ) -> PropertyModel:
        return await self._dal.delete_property(property_id, soft_delete=True)
