from uuid import uuid4

import pytest
from app.components.metrics.dal import MetricDAL
from app.components.metrics.models.metric import MetricModel
from app.components.metrics.models.metric_update import MetricUpdateModel
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError


# Integration test for creating a metric
@pytest.mark.asyncio
async def test_create_metric_integration(metric_dal: MetricDAL, metric_example: MetricModel, metric_set_test_entry):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id

    # Act: Create the metric using the DAL
    created_metric = await metric_dal.create_metric(metric_example)

    # Assert: Check the created metric's data
    assert created_metric.name == metric_example.name
    assert created_metric.status == metric_example.status

    # Assert: Verify the metric exists in the database
    fetched_metric = await metric_dal.get_metric(created_metric.id)
    assert fetched_metric is not None
    assert fetched_metric.id == created_metric.id
    assert fetched_metric.name == created_metric.name


# Integration test for getting a metric by ID
@pytest.mark.asyncio
async def test_get_metric_integration(metric_dal: MetricDAL, metric_example: MetricModel, metric_set_test_entry):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id
    # Act: Create the metric
    created_metric = await metric_dal.create_metric(metric_example)

    # Act: Fetch the metric by ID
    fetched_metric = await metric_dal.get_metric(created_metric.id)

    # Assert: Verify the fetched data matches the created data
    assert fetched_metric.id == created_metric.id
    assert fetched_metric.name == created_metric.name
    assert fetched_metric.status == created_metric.status


# Integration test for getting a non-existent metric
@pytest.mark.asyncio
async def test_get_metric_not_found_integration(metric_dal: MetricDAL):
    # Act & Assert: Ensure fetching a non-existent metric raises an error
    with pytest.raises(DatabaseRecordNotFoundError):
        await metric_dal.get_metric(uuid4())  # Random UUID


# Integration test for finding metrics (non-empty result)
@pytest.mark.asyncio
async def test_find_metrics_non_empty_integration(
    metric_dal: MetricDAL, metric_example: MetricModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id
    # Act: Create a metric
    await metric_dal.create_metric(metric_example)

    # Act: Find metrics
    metrics = await metric_dal.find_metrics()

    # Assert: Verify the result contains at least one metric
    assert len(metrics) > 0
    assert metrics[0].name == metric_example.name


# Integration test for finding metrics (empty result)
@pytest.mark.asyncio
async def test_find_metrics_empty_integration(metric_dal: MetricDAL):
    # Act: Find metrics with an empty database
    metrics = await metric_dal.find_metrics()

    # Assert: The result should be an empty list
    assert len(metrics) == 0


# Integration test for updating a metric
@pytest.mark.asyncio
async def test_update_metric_integration(metric_dal: MetricDAL, metric_example: MetricModel, metric_set_test_entry):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id
    # Act: Create the metric
    created_metric = await metric_dal.create_metric(metric_example)

    # Act: Update the metric
    updated_metric = await metric_dal.update_metric(
        created_metric.id,
        MetricUpdateModel(name="Updated Metric Name"),
    )

    # Assert: Verify the metric was updated correctly
    assert updated_metric.name == "Updated Metric Name"
    assert updated_metric.id == created_metric.id

    # Assert: Fetch and verify the updates
    fetched_metric = await metric_dal.get_metric(created_metric.id)
    assert fetched_metric.name == "Updated Metric Name"


# Integration test for deleting a metric (soft delete)
@pytest.mark.asyncio
async def test_delete_metric_soft_integration(
    metric_dal: MetricDAL, metric_example: MetricModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id
    # Act: Create the metric
    created_metric = await metric_dal.create_metric(metric_example)

    # Act: Soft delete the metric
    deleted_metric = await metric_dal.delete_metric(created_metric.id)

    # Assert: Verify the metric is soft-deleted
    assert deleted_metric.deleted is not None
    assert deleted_metric.id == created_metric.id

    # Assert: Fetch the soft-deleted metric
    fetched_metric = await metric_dal.get_metric(created_metric.id)
    assert fetched_metric.deleted is not None


# Integration test for deleting a metric (permanent delete)
@pytest.mark.asyncio
async def test_delete_metric_permanent_integration(
    metric_dal: MetricDAL, metric_example: MetricModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id
    # Act: Create the metric
    created_metric = await metric_dal.create_metric(metric_example)

    # Act: Permanently delete the metric
    await metric_dal.delete_metric(created_metric.id, soft_delete=False)

    # Assert: Verify the metric no longer exists
    with pytest.raises(DatabaseRecordNotFoundError):
        await metric_dal.get_metric(created_metric.id)
