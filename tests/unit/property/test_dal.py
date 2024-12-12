import pytest
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError

from app.components.properties.dal import PropertyDAL
from app.components.properties.models.property import PropertyModel
from app.components.properties.models.property_update import PropertyUpdateModel


#Tests get_property_by_id
@pytest.mark.asyncio
async def test_get_property_by_id(property_dal: PropertyDAL, property_example: PropertyModel):
    new_property = await property_dal.create_property(property_example)

    retrieved_property = await property_dal.get_property(new_property.id)
    assert retrieved_property.property_name == property_example.property_name
    assert retrieved_property.data_type == property_example.data_type
    assert retrieved_property.property_description == property_example.property_description
    assert retrieved_property.entity_type == property_example.entity_type

@pytest.mark.asyncio
async def test_get_property_by_id_not_found(property_dal: PropertyDAL, property_example: PropertyModel):
    with pytest.raises(DatabaseRecordNotFoundError):
        await property_dal.get_property(property_example.id)


#Tests find_properties
@pytest.mark.asyncio
async def test_find_properties_non_empty(property_dal: PropertyDAL, property_example: PropertyModel):
    new_property_1 = await property_dal.create_property(property_example)

    result = await property_dal.find_properties()

    assert len(result) == 1
    assert result[0].property_name == new_property_1.property_name

@pytest.mark.asyncio
async def test_find_properties_empty(property_dal: PropertyDAL, property_example: PropertyModel):
    result = await property_dal.find_properties()

    assert len(result) == 0


#Tests create_property
@pytest.mark.asyncio
async def test_create_property(property_dal: PropertyDAL, property_example: PropertyModel):
    created_property = await property_dal.create_property(property_example)
    assert created_property.property_name == property_example.property_name
    assert created_property.data_type == property_example.data_type
    assert created_property.property_description == property_example.property_description
    assert created_property.entity_type == property_example.entity_type

#Tests update_property
@pytest.mark.asyncio
async def test_update_property(property_dal: PropertyDAL, property_example: PropertyModel):
    new_property = await property_dal.create_property(property_example)
    updated_property = await property_dal.update_property(new_property.id,
                                                          PropertyUpdateModel(property_name="updated_name"))

    assert updated_property.property_name == "updated_name"


@pytest.mark.asyncio
async def test_update_property_not_found(property_dal: PropertyDAL, property_example: PropertyModel):
    with pytest.raises(DatabaseRecordNotFoundError):
        await property_dal.update_property(property_example.id,
                                           PropertyUpdateModel(property_name="updated_name"))

#Tests delete_property
@pytest.mark.asyncio
async def test_delete_property_soft_delete(property_dal: PropertyDAL, property_example: PropertyModel):
    new_property = await property_dal.create_property(property_example)
    deleted_property = await property_dal.delete_property(new_property.id)

    assert deleted_property.deleted is not None


@pytest.mark.asyncio
async def test_delete_property_hard_delete(property_dal: PropertyDAL, property_example: PropertyModel):
    new_property = await property_dal.create_property(property_example)
    deleted_property = await property_dal.delete_property(new_property.id, False)

    assert deleted_property.deleted is not None
    with pytest.raises(DatabaseRecordNotFoundError):
        await property_dal.get_property(new_property.id)


@pytest.mark.asyncio
async def test_delete_property_not_found(property_dal: PropertyDAL, property_example: PropertyModel):
    with pytest.raises(DatabaseRecordNotFoundError):
        await property_dal.delete_property(property_example.id, False)

