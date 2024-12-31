import pytest
from app.components.metrics.models.metric import MetricModel
from app.components.metrics.models.metric_update import MetricUpdateModel
from app.components.metrics.service import MetricService
from matter_exceptions.exceptions.fastapi import ValidationError


# Integration test for creating a metric
@pytest.mark.asyncio
async def test_create_metric_integration(
    metric_service: MetricService, metric_example: MetricModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id

    # Act: Create the metric using the service
    created_metric = await metric_service.create_metric(metric_example)

    # Assert: Check that the metric returned by the service matches the input
    assert created_metric.name == metric_example.name
    assert created_metric.status == metric_example.status

    # Assert: Check that the metric exists in the database by fetching it
    fetched_metric = await metric_service.get_metric(created_metric.id)
    assert fetched_metric is not None
    assert fetched_metric.id == created_metric.id
    assert fetched_metric.status == created_metric.status
    assert fetched_metric.status == created_metric.status


# Integration test for updating a metric
@pytest.mark.asyncio
async def test_update_metric_integration(
    metric_service: MetricService, metric_example: MetricModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id

    # Act: Create the metric
    new_metric = await metric_service.create_metric(metric_example)

    # Act: Update the created metric
    updated_metric = await metric_service.update_metric(new_metric.id, MetricUpdateModel(name="updated_metric"))

    # Assert: Check that the metric was successfully updated
    assert updated_metric.name == "updated_metric"
    assert updated_metric.id == new_metric.id

    # Assert: Fetch the updated metric from the database to confirm the change
    fetched_metric = await metric_service.get_metric(new_metric.id)
    assert fetched_metric.name == "updated_metric"


# Integration test for deleting a metric (soft delete)
@pytest.mark.asyncio
async def test_delete_metric_integration(
    metric_service: MetricService, metric_example: MetricModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id

    # Act: Create the metric
    new_metric = await metric_service.create_metric(metric_example)

    # Act: Delete the created metric (soft delete)
    deleted_metric = await metric_service.delete_metric(new_metric.id)

    # Assert: The metric should be marked as deleted
    assert deleted_metric.deleted is not None  # assuming 'deleted' is the flag for deletion

    # Assert: Check that the metric is actually marked as deleted in the database
    fetched_metric = await metric_service.get_metric(new_metric.id)
    assert fetched_metric.deleted is not None


# Integration test for finding metrics (non-empty result)
@pytest.mark.asyncio
async def test_find_metrics_non_empty_integration(
    metric_service: MetricService, metric_example: MetricModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_example.metric_set_id = metric_set.id

    # Act: Create a new metric
    await metric_service.create_metric(metric_example)

    # Act: Fetch all metrics
    metrics = await metric_service.find_metrics()

    # Assert: The result should contain the metric we just created
    assert len(metrics) > 0
    assert metrics[0].name == metric_example.name


# Integration test for finding metrics (empty result)
@pytest.mark.asyncio
async def test_find_metrics_empty_integration(metric_service: MetricService):
    # Act: Fetch all metrics when there are none
    metrics = await metric_service.find_metrics()

    # Assert: The result should be empty
    assert len(metrics) == 0


# Integration test for metadata validation during metric creation
@pytest.mark.asyncio
async def test_create_metric_metadata_conversion_integration(
    metric_service: MetricService, metric_example: MetricModel
):
    # Arrange: Add some mock metadata
    metric_example.meta_data = {"key": "value"}

    # Act + Assert: Check that metadata was is rejected
    with pytest.raises(ValidationError):
        await metric_service.create_metric(metric_example)
