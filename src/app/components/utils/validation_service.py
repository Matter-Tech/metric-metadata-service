from matter_exceptions.exceptions.fastapi import ValidationError
from matter_observability.metrics import count_occurrence, measure_processing_time

from app.common.enums.enums import EntityTypeEnum
from app.components.properties.dal import PropertyDAL
from app.components.properties.service import PropertyService


class ValidationService:
    def __init__(
        self,
        property_service: PropertyService,
    ):
        self._property_service = property_service


    @count_occurrence(label="utils.validate_metadata")
    @measure_processing_time(label="utils.validate_metadata")
    async def validate_metadata(
        self,
        entity_type: EntityTypeEnum,
        meta_data: dict,
    ) -> None:
        valid_properties = await self._property_service.find_properties(
            filters={"entity_type": EntityTypeEnum.METRIC_SET})
        valid_property_names = [prop.property_name for prop in valid_properties]
        invalid_keys = [key for key in meta_data if key not in valid_property_names]

        if invalid_keys:
            raise ValidationError(description=f"Cannot create {entity_type.value} with meta_data: {meta_data}.",
                                  detail={
                                      "invalid_keys": invalid_keys,
                                      "valid_keys": valid_property_names
                                  }, )