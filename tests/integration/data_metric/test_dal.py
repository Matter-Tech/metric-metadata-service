from uuid import uuid4

import pytest
from app.components.data_metrics.dal import DataMetricDAL
from app.components.data_metrics.models.data_metric import DataMetricModel
from app.components.data_metrics.models.data_metric_update import DataMetricUpdateModel
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError


# Integration test for creating a data metric
@pytest.mark.asyncio
async def test_create_data_metric_integration(data_metric_dal: DataMetricDAL, data_metric_example: DataMetricModel):
    # Act: Create the data metric using the DAL method
    created_data_metric = await data_metric_dal.create_data_metric(data_metric_example)

    # Assert: Check that the data metric has been created with the correct data
    assert created_data_metric.name == data_metric_example.name
    assert created_data_metric.data_id == data_metric_example.data_id

    # Assert: Check that the data metric exists in the database by fetching it
    fetched_data_metric = await data_metric_dal.get_data_metric(created_data_metric.id)
    assert fetched_data_metric is not None
    assert fetched_data_metric.id == created_data_metric.id
    assert fetched_data_metric.name == created_data_metric.name
    assert fetched_data_metric.data_id == created_data_metric.data_id


# Integration test for getting a data metric by ID
@pytest.mark.asyncio
async def test_get_data_metric_integration(data_metric_dal: DataMetricDAL, data_metric_example: DataMetricModel):
    # Act: Create the data metric using the DAL method
    created_data_metric = await data_metric_dal.create_data_metric(data_metric_example)

    # Act: Retrieve the data metric by ID
    fetched_data_metric = await data_metric_dal.get_data_metric(created_data_metric.id)

    # Assert: Verify the fetched data metric matches the created one
    assert fetched_data_metric.id == created_data_metric.id
    assert fetched_data_metric.name == created_data_metric.name
    assert fetched_data_metric.data_id == created_data_metric.data_id


# Integration test for getting a data metric that does not exist
@pytest.mark.asyncio
async def test_get_data_metric_not_found_integration(data_metric_dal: DataMetricDAL):
    # Act & Assert: Ensure trying to fetch a non-existing data metric raises an error
    with pytest.raises(DatabaseRecordNotFoundError):
        await data_metric_dal.get_data_metric(uuid4())  # Using a random UUID


# Integration test for finding data metrics (non-empty result)
@pytest.mark.asyncio
async def test_find_data_metrics_non_empty_integration(
    data_metric_dal: DataMetricDAL, data_metric_example: DataMetricModel
):
    # Act: Create a data metric using the DAL method
    await data_metric_dal.create_data_metric(data_metric_example)

    # Act: Find data metrics in the database
    data_metrics = await data_metric_dal.find_data_metrics()

    # Assert: Ensure the result contains at least one data metric
    assert len(data_metrics) > 0
    assert data_metrics[0].name == data_metric_example.name


# Integration test for finding data metrics (empty result)
@pytest.mark.asyncio
async def test_find_data_metrics_empty_integration(data_metric_dal: DataMetricDAL):
    # Act: Find data metrics when there are no entries in the database
    data_metrics = await data_metric_dal.find_data_metrics()

    # Assert: The result should be empty
    assert len(data_metrics) == 0


# Integration test for updating a data metric
@pytest.mark.asyncio
async def test_update_data_metric_integration(data_metric_dal: DataMetricDAL, data_metric_example: DataMetricModel):
    # Act: Create the data metric
    created_data_metric = await data_metric_dal.create_data_metric(data_metric_example)

    # Act: Update the data metric
    updated_data_metric = await data_metric_dal.update_data_metric(
        created_data_metric.id, DataMetricUpdateModel(name="Updated Metric")
    )

    # Assert: Ensure the data metric is updated correctly
    assert updated_data_metric.name == "Updated Metric"
    assert updated_data_metric.id == created_data_metric.id

    # Assert: Fetch the updated data metric and verify changes
    fetched_data_metric = await data_metric_dal.get_data_metric(created_data_metric.id)
    assert fetched_data_metric.name == "Updated Metric"


# Integration test for deleting a data metric (soft delete)
@pytest.mark.asyncio
async def test_delete_data_metric_integration(data_metric_dal: DataMetricDAL, data_metric_example: DataMetricModel):
    # Act: Create the data metric
    created_data_metric = await data_metric_dal.create_data_metric(data_metric_example)

    # Act: Soft delete the data metric
    deleted_data_metric = await data_metric_dal.delete_data_metric(created_data_metric.id)

    # Assert: Ensure the data metric is marked as deleted
    assert deleted_data_metric.deleted is not None
    assert deleted_data_metric.id == created_data_metric.id

    # Assert: Fetch the data metric and check if it is soft-deleted
    fetched_data_metric = await data_metric_dal.get_data_metric(created_data_metric.id)
    assert fetched_data_metric.deleted is not None


# Integration test for deleting a data metric (permanent delete)
@pytest.mark.asyncio
async def test_permanent_delete_data_metric_integration(
    data_metric_dal: DataMetricDAL, data_metric_example: DataMetricModel
):
    # Act: Create the data metric
    created_data_metric = await data_metric_dal.create_data_metric(data_metric_example)

    # Act: Permanently delete the data metric
    await data_metric_dal.delete_data_metric(created_data_metric.id, soft_delete=False)

    # Assert: The data metric should not exist after being permanently deleted
    with pytest.raises(DatabaseRecordNotFoundError):
        await data_metric_dal.get_data_metric(created_data_metric.id)
