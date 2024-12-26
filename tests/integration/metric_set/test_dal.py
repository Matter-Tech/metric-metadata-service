from uuid import uuid4

import pytest
from app.components.metric_sets.dal import MetricSetDAL
from app.components.metric_sets.models.metric_set import MetricSetModel
from app.components.metric_sets.models.metric_set_update import MetricSetUpdateModel
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError


# Integration test for creating a metric set
@pytest.mark.asyncio
async def test_create_metric_set_integration(metric_set_dal: MetricSetDAL, metric_set_example: MetricSetModel):
    # Act: Create the metric set
    created_metric_set = await metric_set_dal.create_metric_set(metric_set_example)

    # Assert: Check the created metric set's data
    assert created_metric_set.name == metric_set_example.name
    assert created_metric_set.description == metric_set_example.description

    # Assert: Verify the metric set exists in the database
    fetched_metric_set = await metric_set_dal.get_metric_set(created_metric_set.id)
    assert fetched_metric_set is not None
    assert fetched_metric_set.id == created_metric_set.id
    assert fetched_metric_set.name == created_metric_set.name


# Integration test for getting a metric set by ID
@pytest.mark.asyncio
async def test_get_metric_set_integration(metric_set_dal: MetricSetDAL, metric_set_example: MetricSetModel):
    # Act: Create the metric set
    created_metric_set = await metric_set_dal.create_metric_set(metric_set_example)

    # Act: Fetch the metric set by ID
    fetched_metric_set = await metric_set_dal.get_metric_set(created_metric_set.id)

    # Assert: Verify the fetched data matches the created data
    assert fetched_metric_set.id == created_metric_set.id
    assert fetched_metric_set.name == created_metric_set.name
    assert fetched_metric_set.description == created_metric_set.description


# Integration test for getting a non-existent metric set
@pytest.mark.asyncio
async def test_get_metric_set_not_found_integration(metric_set_dal: MetricSetDAL):
    # Act & Assert: Ensure fetching a non-existent metric set raises an error
    with pytest.raises(DatabaseRecordNotFoundError):
        await metric_set_dal.get_metric_set(uuid4())  # Random UUID


# Integration test for finding metric sets (non-empty result)
@pytest.mark.asyncio
async def test_find_metric_sets_non_empty_integration(metric_set_dal: MetricSetDAL, metric_set_example: MetricSetModel):
    # Act: Create a metric set
    await metric_set_dal.create_metric_set(metric_set_example)

    # Act: Find metric sets
    metric_sets = await metric_set_dal.find_metric_sets()

    # Assert: Verify the result contains at least one metric set
    assert len(metric_sets) > 0
    assert metric_sets[0].name == metric_set_example.name


# Integration test for finding metric sets (empty result)
@pytest.mark.asyncio
async def test_find_metric_sets_empty_integration(metric_set_dal: MetricSetDAL):
    # Act: Find metric sets with an empty database
    metric_sets = await metric_set_dal.find_metric_sets()

    # Assert: The result should be an empty list
    assert len(metric_sets) == 0


# Integration test for updating a metric set
@pytest.mark.asyncio
async def test_update_metric_set_integration(metric_set_dal: MetricSetDAL, metric_set_example: MetricSetModel):
    # Act: Create the metric set
    created_metric_set = await metric_set_dal.create_metric_set(metric_set_example)

    # Act: Update the metric set
    updated_metric_set = await metric_set_dal.update_metric_set(
        created_metric_set.id,
        MetricSetUpdateModel(name="Updated Metric Set"),
    )

    # Assert: Verify the metric set was updated correctly
    assert updated_metric_set.name == "Updated Metric Set"
    assert updated_metric_set.id == created_metric_set.id

    # Assert: Fetch and verify the updates
    fetched_metric_set = await metric_set_dal.get_metric_set(created_metric_set.id)
    assert fetched_metric_set.name == "Updated Metric Set"


# Integration test for deleting a metric set (soft delete)
@pytest.mark.asyncio
async def test_delete_metric_set_soft_integration(metric_set_dal: MetricSetDAL, metric_set_example: MetricSetModel):
    # Act: Create the metric set
    created_metric_set = await metric_set_dal.create_metric_set(metric_set_example)

    # Act: Soft delete the metric set
    deleted_metric_set = await metric_set_dal.delete_metric_set(created_metric_set.id)

    # Assert: Verify the metric set is soft-deleted
    assert deleted_metric_set.deleted is not None
    assert deleted_metric_set.id == created_metric_set.id

    # Assert: Fetch the soft-deleted metric set
    fetched_metric_set = await metric_set_dal.get_metric_set(created_metric_set.id)
    assert fetched_metric_set.deleted is not None


# Integration test for deleting a metric set (permanent delete)
@pytest.mark.asyncio
async def test_delete_metric_set_permanent_integration(
    metric_set_dal: MetricSetDAL, metric_set_example: MetricSetModel
):
    # Act: Create the metric set
    created_metric_set = await metric_set_dal.create_metric_set(metric_set_example)

    # Act: Permanently delete the metric set
    await metric_set_dal.delete_metric_set(created_metric_set.id, soft_delete=False)

    # Assert: Verify the metric set no longer exists
    with pytest.raises(DatabaseRecordNotFoundError):
        await metric_set_dal.get_metric_set(created_metric_set.id)
