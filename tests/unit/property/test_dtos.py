from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.common.enums.enums import EntityTypeEnum, DataTypeEnum
from app.components.properties.dtos import PropertyListOutDTO, PropertyDeletionOutDTO, FullPropertyOutDTO, PropertyUpdateInDTO, PropertyInDTO

def get_valid_property_data():
    return {
        "propertyName": "ValidName",
        "propertyDescription": "A valid description",
        "dataType": DataTypeEnum.STRING,
        "entityType": EntityTypeEnum.METRIC,
        "isRequired": True
    }

# Tests for PropertyInDTO
def test_property_in_dto_valid():
    data = get_valid_property_data()
    dto = PropertyInDTO(**data)
    assert dto.property_name == "ValidName"
    assert dto.property_description == "A valid description"
    assert dto.data_type == DataTypeEnum.STRING
    assert dto.entity_type == EntityTypeEnum.METRIC
    assert dto.is_required is True

def test_property_in_dto_invalid_property_name_with_spaces():
    data = get_valid_property_data()
    data["propertyName"] = "Invalid Name"
    with pytest.raises(ValidationError, match="Property Name must only contain alphabetic characters"):
        PropertyInDTO(**data)

def test_property_in_dto_invalid_property_name_with_numbers():
    data = get_valid_property_data()
    data["propertyName"] = "Name123"
    with pytest.raises(ValidationError, match="Property Name must only contain alphabetic characters"):
        PropertyInDTO(**data)

def test_property_in_dto_invalid_property_description_whitespace():
    data = get_valid_property_data()
    data["propertyDescription"] = "   "
    with pytest.raises(ValidationError, match="Property Description cannot be only whitespace"):
        PropertyInDTO(**data)

# Tests for PropertyUpdateInDTO
def test_property_update_in_dto_valid_partial_update():
    data = {
        "propertyName": None,
        "propertyDescription": "Updated description",
        "dataType": None,
        "entityType": EntityTypeEnum.METRIC,
        "isRequired": None
    }
    dto = PropertyUpdateInDTO(**data)
    assert dto.property_name is None
    assert dto.property_description == "Updated description"
    assert dto.data_type is None
    assert dto.entity_type == EntityTypeEnum.METRIC
    assert dto.is_required is None

def test_property_update_in_dto_invalid_property_name():
    data = {"propertyName": "Invalid Name"}
    with pytest.raises(ValidationError, match="Property Name must only contain alphabetic characters"):
        PropertyUpdateInDTO(**data)

def test_property_update_in_dto_invalid_property_description_whitespace():
    data = {"propertyDescription": "   "}
    with pytest.raises(ValidationError, match="Property Description cannot be only whitespace"):
        PropertyUpdateInDTO(**data)

# Tests for FullPropertyOutDTO
def test_full_property_out_dto_valid():
    data = {
        "id": uuid4(),
        "propertyName": "ValidName",
        "propertyDescription": "Valid description",
        "dataType": DataTypeEnum.STRING,
        "entityType": EntityTypeEnum.METRIC,
        "isRequired": True
    }
    dto = FullPropertyOutDTO(**data)
    assert dto.id
    assert dto.property_name == "ValidName"
    assert dto.property_description == "Valid description"
    assert dto.data_type == DataTypeEnum.STRING
    assert dto.entity_type == EntityTypeEnum.METRIC
    assert dto.is_required is True

# Tests for PropertyDeletionOutDTO
def test_property_deletion_out_dto_valid():
    data = {
        "id": uuid4(),
        "deletedAt": datetime.now(tz=timezone.utc)
    }
    dto = PropertyDeletionOutDTO(**data)
    assert dto.id
    assert dto.deleted_at

# Tests for PropertyListOutDTO
def test_property_list_out_dto_valid():
    data = {
        "count": 2,
        "properties": [
            {
                "id": uuid4(),
                "propertyName": "ValidName1",
                "propertyDescription": "Valid description 1",
                "dataType": DataTypeEnum.STRING,
                "entityType": EntityTypeEnum.METRIC,
                "isRequired": True
            },
            {
                "id": uuid4(),
                "propertyName": "ValidName2",
                "propertyDescription": "Valid description 2",
                "dataType": DataTypeEnum.NUMBER,
                "entityType": EntityTypeEnum.METRIC_SET,
                "isRequired": False
            }
        ]
    }
    dto = PropertyListOutDTO(**data)
    assert dto.count == 2
    assert len(dto.properties) == 2
    assert dto.properties[0].property_name == "ValidName1"
    assert dto.properties[1].data_type == DataTypeEnum.NUMBER