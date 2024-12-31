import pytest
from app.components.metric_sets.models.metric_set import MetricSetModel
from app.components.metric_sets.models.metric_set_update import MetricSetUpdateModel
from app.components.metric_sets.service import MetricSetService
from matter_exceptions.exceptions.fastapi import ValidationError


# Integration test for creating a metric set
@pytest.mark.asyncio
async def test_create_metric_set_integration(metric_set_service: MetricSetService, metric_set_example: MetricSetModel):
    # Act: Create a metric set
    created_metric_set = await metric_set_service.create_metric_set(metric_set_example)

    # Assert: Check that the metric set returned by the service matches the input
    assert created_metric_set.short_name == metric_set_example.short_name
    assert created_metric_set.status == metric_set_example.status

    # Assert: Fetch the metric set from the database to confirm it exists
    fetched_metric_set = await metric_set_service.get_metric_set(created_metric_set.id)
    assert fetched_metric_set is not None
    assert fetched_metric_set.id == created_metric_set.id


# Integration test for updating a metric set
@pytest.mark.asyncio
async def test_update_metric_set_integration(metric_set_service: MetricSetService, metric_set_example: MetricSetModel):
    # Act: Create a metric set
    new_metric_set = await metric_set_service.create_metric_set(metric_set_example)

    # Act: Update the created metric set
    updated_metric_set = await metric_set_service.update_metric_set(
        new_metric_set.id, MetricSetUpdateModel(short_name="updated_metric_set")
    )

    # Assert: Check that the update was successful
    assert updated_metric_set.short_name == "updated_metric_set"
    assert updated_metric_set.id == new_metric_set.id

    # Assert: Fetch the updated metric set to confirm the change
    fetched_metric_set = await metric_set_service.get_metric_set(new_metric_set.id)
    assert fetched_metric_set.short_name == "updated_metric_set"


# Integration test for deleting a metric set (soft delete)
@pytest.mark.asyncio
async def test_delete_metric_set_integration(metric_set_service: MetricSetService, metric_set_example: MetricSetModel):
    # Act: Create a metric set
    new_metric_set = await metric_set_service.create_metric_set(metric_set_example)

    # Act: Soft delete the metric set
    deleted_metric_set = await metric_set_service.delete_metric_set(new_metric_set.id)

    # Assert: Check the metric set is marked as deleted
    assert deleted_metric_set.deleted is not None

    # Assert: Verify it is still fetchable but marked as deleted
    fetched_metric_set = await metric_set_service.get_metric_set(new_metric_set.id)
    assert fetched_metric_set.deleted is not None


# Integration test for finding metric sets (non-empty result)
@pytest.mark.asyncio
async def test_find_metric_sets_non_empty_integration(
    metric_set_service: MetricSetService, metric_set_example: MetricSetModel
):
    # Act: Create a new metric set
    await metric_set_service.create_metric_set(metric_set_example)

    # Act: Fetch all metric sets
    metric_sets = await metric_set_service.find_metric_sets()

    # Assert: The result should include the created metric set
    assert len(metric_sets) > 0
    assert any(metric_set.short_name == metric_set_example.short_name for metric_set in metric_sets)


# Integration test for finding metric sets (empty result)
@pytest.mark.asyncio
async def test_find_metric_sets_empty_integration(metric_set_service: MetricSetService):
    # Act: Fetch all metric sets when there are none
    metric_sets = await metric_set_service.find_metric_sets()

    # Assert: The result should be empty
    assert len(metric_sets) == 0


# Integration test for metadata validation during metric set creation
@pytest.mark.asyncio
async def test_create_metric_set_metadata_conversion_integration(
    metric_set_service: MetricSetService, metric_set_example: MetricSetModel
):
    # Arrange: Add invalid metadata
    metric_set_example.meta_data = {"invalid_key": "invalid_value"}

    # Act + Assert: Ensure a ValidationError is raised
    with pytest.raises(ValidationError):
        await metric_set_service.create_metric_set(metric_set_example)
