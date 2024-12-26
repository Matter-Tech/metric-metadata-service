from uuid import uuid4

import pytest
from app.components.properties.dal import PropertyDAL
from app.components.properties.models.property import PropertyModel
from app.components.properties.models.property_update import PropertyUpdateModel
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError


# Integration test for creating a property
@pytest.mark.asyncio
async def test_create_property_integration(property_dal: PropertyDAL, property_example: PropertyModel):
    # Act: Create the property using the DAL method
    created_property = await property_dal.create_property(property_example)

    # Assert: Check that the property has been created with the correct data
    assert created_property.property_name == property_example.property_name
    assert created_property.data_type == property_example.data_type
    assert created_property.property_description == property_example.property_description
    assert created_property.entity_type == property_example.entity_type

    # Assert: Check that the property exists in the database by fetching it
    fetched_property = await property_dal.get_property(created_property.id)
    assert fetched_property is not None
    assert fetched_property.id == created_property.id
    assert fetched_property.property_name == created_property.property_name
    assert fetched_property.data_type == created_property.data_type


# Integration test for getting a property by ID
@pytest.mark.asyncio
async def test_get_property_integration(property_dal: PropertyDAL, property_example: PropertyModel):
    # Act: Create the property using the DAL method
    created_property = await property_dal.create_property(property_example)

    # Act: Retrieve the property by ID
    fetched_property = await property_dal.get_property(created_property.id)

    # Assert: Verify the fetched property matches the created one
    assert fetched_property.id == created_property.id
    assert fetched_property.property_name == created_property.property_name
    assert fetched_property.data_type == created_property.data_type


# Integration test for getting a property that does not exist
@pytest.mark.asyncio
async def test_get_property_not_found_integration(property_dal: PropertyDAL):
    # Act & Assert: Ensure trying to fetch a non-existing property raises an error
    with pytest.raises(DatabaseRecordNotFoundError):
        await property_dal.get_property(uuid4())  # Using a random UUID


# Integration test for finding properties (non-empty result)
@pytest.mark.asyncio
async def test_find_properties_non_empty_integration(property_dal: PropertyDAL, property_example: PropertyModel):
    # Act: Create a property using the DAL method
    await property_dal.create_property(property_example)

    # Act: Find properties in the database
    properties = await property_dal.find_properties()

    # Assert: Ensure the result contains at least one property
    assert len(properties) > 0
    assert properties[0].property_name == property_example.property_name


# Integration test for finding properties (empty result)
@pytest.mark.asyncio
async def test_find_properties_empty_integration(property_dal: PropertyDAL):
    # Act: Find properties when there are no entries in the database
    properties = await property_dal.find_properties()

    # Assert: The result should be empty
    assert len(properties) == 0


# Integration test for updating a property
@pytest.mark.asyncio
async def test_update_property_integration(property_dal: PropertyDAL, property_example: PropertyModel):
    # Act: Create the property
    created_property = await property_dal.create_property(property_example)

    # Act: Update the property
    updated_property = await property_dal.update_property(
        created_property.id, PropertyUpdateModel(property_name="Updated Property")
    )

    # Assert: Ensure the property is updated correctly
    assert updated_property.property_name == "Updated Property"
    assert updated_property.id == created_property.id

    # Assert: Fetch the updated property and verify changes
    fetched_property = await property_dal.get_property(created_property.id)
    assert fetched_property.property_name == "Updated Property"


# Integration test for deleting a property (soft delete)
@pytest.mark.asyncio
async def test_delete_property_integration(property_dal: PropertyDAL, property_example: PropertyModel):
    # Act: Create the property
    created_property = await property_dal.create_property(property_example)

    # Act: Soft delete the property
    deleted_property = await property_dal.delete_property(created_property.id)

    # Assert: Ensure the property is marked as deleted
    assert deleted_property.deleted is not None  # assuming 'deleted' is the flag for soft delete
    assert deleted_property.id == created_property.id

    # Assert: Fetch the property and check if it is soft-deleted
    fetched_property = await property_dal.get_property(created_property.id)
    assert fetched_property.deleted is not None


# Integration test for deleting a property (permanent delete)
@pytest.mark.asyncio
async def test_permanent_delete_property_integration(property_dal: PropertyDAL, property_example: PropertyModel):
    # Act: Create the property
    created_property = await property_dal.create_property(property_example)

    # Act: Permanently delete the property
    await property_dal.delete_property(created_property.id, soft_delete=False)

    # Assert: The property should not exist after being permanently deleted
    with pytest.raises(DatabaseRecordNotFoundError):
        await property_dal.get_property(created_property.id)
