from matter_exceptions.exceptions.fastapi import ValidationError
from matter_observability.metrics import count_occurrence, measure_processing_time

from app.common.enums.enums import EntityTypeEnum
from app.components.properties.service import PropertyService


class MetaDataService:
    def __init__(
        self,
        property_service: PropertyService,
    ):
        self._property_service = property_service

    @count_occurrence(label="utils.validate_metadata")
    @measure_processing_time(label="utils.validate_metadata")
    async def convert_metadata_names_to_ids(
        self,
        entity_type: EntityTypeEnum,
        meta_data: dict,
    ) -> dict:
        property_name_to_id = {
            prop.property_name: str(prop.id)
            for prop in await self._property_service.find_properties(
                filters={"entity_type": entity_type}
            )
        }

        invalid_keys = set(meta_data) - set(property_name_to_id)
        if invalid_keys:
            raise ValidationError(
                description=f"Cannot create {entity_type.value} with meta_data: {meta_data}.",
                detail={"invalid_keys": list(invalid_keys), "valid_keys": list(property_name_to_id.keys())},
            )

        return {property_name_to_id[key]: value for key, value in meta_data.items()}


    @count_occurrence(label="utils.transform_metadata")
    @measure_processing_time(label="utils.transform_metadata")
    async def convert_metadata_ids_to_names(
            self,
            entity_type: EntityTypeEnum,
            meta_data: dict,
    ) -> dict:
        # Fetch property mappings for the entity type
        property_id_to_name = {
            str(prop.id): prop.property_name
            for prop in await self._property_service.find_properties(
                filters={"entity_type": entity_type}
            )
        }

        # Transform metadata
        return {
            property_id_to_name.get(property_id, property_id): value
            for property_id, value in meta_data.items()
        }