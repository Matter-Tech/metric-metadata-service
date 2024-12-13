import pytest
from app.components.properties.models.property import PropertyModel
from app.components.properties.models.property_update import PropertyUpdateModel
from app.components.properties.service import PropertyService


# Integration test for creating a property
@pytest.mark.asyncio
async def test_create_property_integration(property_service: PropertyService, property_example: PropertyModel):
    # Act: Create the property using the service
    created_property = await property_service.create_property(property_example)

    # Assert: Check that the property returned by the service has the same values as the input
    assert created_property.property_name == property_example.property_name
    assert created_property.data_type == property_example.data_type
    assert created_property.property_description == property_example.property_description
    assert created_property.entity_type == property_example.entity_type

    # Assert: Check that the property actually exists in the database by fetching it
    fetched_property = await property_service.get_property(created_property.id)
    assert fetched_property is not None
    assert fetched_property.id == created_property.id
    assert fetched_property.property_name == created_property.property_name
    assert fetched_property.data_type == created_property.data_type


# Integration test for updating a property
@pytest.mark.asyncio
async def test_update_property_integration(property_service: PropertyService, property_example: PropertyModel):
    # Act: Create the property
    new_property = await property_service.create_property(property_example)

    # Act: Update the created property
    updated_property = await property_service.update_property(
        new_property.id, PropertyUpdateModel(property_name="Updated Property")
    )

    # Assert: Check that the property was successfully updated
    assert updated_property.property_name == "Updated Property"
    assert updated_property.id == new_property.id

    # Assert: Fetch the updated property from the database to confirm the change
    fetched_property = await property_service.get_property(new_property.id)
    assert fetched_property.property_name == "Updated Property"


# Integration test for deleting a property (soft delete)
@pytest.mark.asyncio
async def test_delete_property_integration(property_service: PropertyService, property_example: PropertyModel):
    # Act: Create the property
    new_property = await property_service.create_property(property_example)

    # Act: Delete the created property (soft delete)
    deleted_property = await property_service.delete_property(new_property.id)

    # Assert: The property should be marked as deleted
    assert deleted_property.deleted is not None  # assuming 'deleted' is the flag for deletion

    # Assert: Check that the property is actually marked as deleted in the database
    fetched_property = await property_service.get_property(new_property.id)
    assert fetched_property.deleted is not None


# Integration test for finding properties (non-empty result)
@pytest.mark.asyncio
async def test_find_properties_non_empty_integration(
    property_service: PropertyService, property_example: PropertyModel
):
    # Act: Create a new property
    await property_service.create_property(property_example)

    # Act: Fetch all properties
    properties = await property_service.find_properties()

    # Assert: The result should contain the property we just created
    assert len(properties) > 0
    assert properties[0].property_name == property_example.property_name


# Integration test for finding properties (empty result)
@pytest.mark.asyncio
async def test_find_properties_empty_integration(property_service: PropertyService):
    # Act: Fetch all properties when there are none
    properties = await property_service.find_properties()

    # Assert: The result should be empty
    assert len(properties) == 0
