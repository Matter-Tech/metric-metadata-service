import pytest
from app.components.data_metrics.models.data_metric import DataMetricModel
from app.components.data_metrics.models.data_metric_update import DataMetricUpdateModel
from app.components.data_metrics.service import DataMetricService
from matter_exceptions.exceptions.fastapi import ValidationError


# Integration test for creating a data metric
@pytest.mark.asyncio
async def test_create_data_metric_integration(
    data_metric_service: DataMetricService, data_metric_example: DataMetricModel
):
    # Act: Create the data metric using the service
    created_data_metric = await data_metric_service.create_data_metric(data_metric_example)

    # Assert: Check that the data metric returned by the service matches the input
    assert created_data_metric.name == data_metric_example.name
    assert created_data_metric.metric_type == data_metric_example.metric_type

    # Assert: Check that the data metric exists in the database by fetching it
    fetched_data_metric = await data_metric_service.get_data_metric(created_data_metric.id)
    assert fetched_data_metric is not None
    assert fetched_data_metric.id == created_data_metric.id
    assert fetched_data_metric.metric_type == created_data_metric.metric_type


# Integration test for updating a data metric
@pytest.mark.asyncio
async def test_update_data_metric_integration(
    data_metric_service: DataMetricService, data_metric_example: DataMetricModel
):
    # Act: Create the data metric
    new_data_metric = await data_metric_service.create_data_metric(data_metric_example)

    # Act: Update the created data metric
    updated_data_metric = await data_metric_service.update_data_metric(
        new_data_metric.id, DataMetricUpdateModel(name="updated_data_metric")
    )

    # Assert: Check that the data metric was successfully updated
    assert updated_data_metric.name == "updated_data_metric"
    assert updated_data_metric.id == new_data_metric.id

    # Assert: Fetch the updated data metric from the database to confirm the change
    fetched_data_metric = await data_metric_service.get_data_metric(new_data_metric.id)
    assert fetched_data_metric.name == "updated_data_metric"


# Integration test for deleting a data metric (soft delete)
@pytest.mark.asyncio
async def test_delete_data_metric_integration(
    data_metric_service: DataMetricService, data_metric_example: DataMetricModel
):
    # Act: Create the data metric
    new_data_metric = await data_metric_service.create_data_metric(data_metric_example)

    # Act: Delete the created data metric (soft delete)
    deleted_data_metric = await data_metric_service.delete_data_metric(new_data_metric.id)

    # Assert: The data metric should be marked as deleted
    assert deleted_data_metric.deleted is not None  # assuming 'deleted' is the flag for deletion

    # Assert: Check that the data metric is actually marked as deleted in the database
    fetched_data_metric = await data_metric_service.get_data_metric(new_data_metric.id)
    assert fetched_data_metric.deleted is not None


# Integration test for finding data metrics (non-empty result)
@pytest.mark.asyncio
async def test_find_data_metrics_non_empty_integration(
    data_metric_service: DataMetricService, data_metric_example: DataMetricModel
):
    # Act: Create a new data metric
    await data_metric_service.create_data_metric(data_metric_example)

    # Act: Fetch all data metrics
    data_metrics = await data_metric_service.find_data_metrics()

    # Assert: The result should contain the data metric we just created
    assert len(data_metrics) > 0
    assert data_metrics[0].name == data_metric_example.name


# Integration test for finding data metrics (empty result)
@pytest.mark.asyncio
async def test_find_data_metrics_empty_integration(data_metric_service: DataMetricService):
    # Act: Fetch all data metrics when there are none
    data_metrics = await data_metric_service.find_data_metrics()

    # Assert: The result should be empty
    assert len(data_metrics) == 0


# Integration test for metadata validation during data metric creation
@pytest.mark.asyncio
async def test_create_data_metric_metadata_conversion_integration(
    data_metric_service: DataMetricService, data_metric_example: DataMetricModel
):
    # Arrange: Add some mock metadata
    data_metric_example.meta_data = {"invalid_key": "invalid_value"}

    # Act + Assert: Check that invalid metadata is rejected
    with pytest.raises(ValidationError):
        await data_metric_service.create_data_metric(data_metric_example)
