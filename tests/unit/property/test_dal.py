import pytest

from app.components.properties.dal import PropertyDAL


@pytest.mark.asyncio
async def test_create_property(property_dal: PropertyDAL):
    property_data = {
        "property_name": "TestProperty",
        "property_description": "Description",
        "data_type": "string",
        "entity_type": "metric",
        "is_required": True,
    }
    created_property = await property_dal.create_property(**property_data)
    assert created_property.property_name == "TestProperty"
    assert created_property.data_type == "string"


@pytest.mark.asyncio
async def test_get_property_by_id(property_dal: PropertyDAL):
    property_data = {
        "property_name": "TestProperty",
        "property_description": "Description",
        "data_type": "string",
        "entity_type": "metric",
        "is_required": True,
    }
    new_property = await property_dal.create_property(**property_data)

    # Retrieve property
    retrieved_property = await property_dal.get_property(new_property.id)
    assert retrieved_property.property_name == "TestProperty"