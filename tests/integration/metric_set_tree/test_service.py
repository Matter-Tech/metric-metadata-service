import pytest
from app.components.metric_set_trees.models.metric_set_tree import MetricSetTreeModel
from app.components.metric_set_trees.models.metric_set_trees_update import MetricSetTreeUpdateModel
from app.components.metric_set_trees.service import MetricSetTreeService
from matter_exceptions.exceptions.fastapi import ValidationError


# Integration test for creating a metric set tree
@pytest.mark.asyncio
async def test_create_metric_set_tree_integration(
    metric_set_tree_service: MetricSetTreeService, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id

    # Act: Create a metric set tree
    created_metric_set_tree = await metric_set_tree_service.create_metric_set_tree(metric_set_tree_example)

    # Assert: Check that the metric set tree returned by the service matches the input
    assert created_metric_set_tree.node_name == metric_set_tree_example.node_name
    assert created_metric_set_tree.node_description == metric_set_tree_example.node_description

    # Assert: Fetch the metric set tree from the database to confirm it exists
    fetched_metric_set_tree = await metric_set_tree_service.get_metric_set_tree(created_metric_set_tree.id)
    assert fetched_metric_set_tree is not None
    assert fetched_metric_set_tree.id == created_metric_set_tree.id


# Integration test for updating a metric set tree
@pytest.mark.asyncio
async def test_update_metric_set_tree_integration(
    metric_set_tree_service: MetricSetTreeService, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id

    # Act: Create a metric set tree
    new_metric_set_tree = await metric_set_tree_service.create_metric_set_tree(metric_set_tree_example)

    # Act: Update the created metric set tree
    updated_metric_set_tree = await metric_set_tree_service.update_metric_set_tree(
        new_metric_set_tree.id, MetricSetTreeUpdateModel(node_name="Updated Metric Set Tree")
    )

    # Assert: Check that the update was successful
    assert updated_metric_set_tree.node_name == "Updated Metric Set Tree"
    assert updated_metric_set_tree.id == new_metric_set_tree.id


# Integration test for deleting a metric set tree (soft delete)
@pytest.mark.asyncio
async def test_delete_metric_set_tree_integration(
    metric_set_tree_service: MetricSetTreeService, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id

    # Act: Create a metric set tree
    new_metric_set_tree = await metric_set_tree_service.create_metric_set_tree(metric_set_tree_example)

    # Act: Soft delete the metric set tree
    deleted_metric_set_tree = await metric_set_tree_service.delete_metric_set_tree(new_metric_set_tree.id)

    # Assert: Check the metric set tree is marked as deleted
    assert deleted_metric_set_tree.deleted is not None

    # Assert: Verify it is still fetchable but marked as deleted
    fetched_metric_set_tree = await metric_set_tree_service.get_metric_set_tree(new_metric_set_tree.id)
    assert fetched_metric_set_tree.deleted is not None


# Integration test for finding metric set trees (non-empty result)
@pytest.mark.asyncio
async def test_find_metric_set_trees_non_empty_integration(
    metric_set_tree_service: MetricSetTreeService, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id

    # Act: Create a new metric set tree
    await metric_set_tree_service.create_metric_set_tree(metric_set_tree_example)

    # Act: Fetch all metric set trees
    metric_set_trees = await metric_set_tree_service.find_metric_set_trees()

    # Assert: The result should include the created metric set tree
    assert len(metric_set_trees) > 0
    assert any(metric_set_tree.node_name == metric_set_tree_example.node_name for metric_set_tree in metric_set_trees)


# Integration test for finding metric set trees (empty result)
@pytest.mark.asyncio
async def test_find_metric_set_trees_empty_integration(metric_set_tree_service: MetricSetTreeService):
    # Act: Fetch all metric set trees when there are none
    metric_set_trees = await metric_set_tree_service.find_metric_set_trees()

    # Assert: The result should be empty
    assert len(metric_set_trees) == 0


# Integration test for metadata validation during metric set tree creation
@pytest.mark.asyncio
async def test_create_metric_set_tree_metadata_validation_integration(
    metric_set_tree_service: MetricSetTreeService, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id

    # Arrange: Add invalid metadata
    metric_set_tree_example.meta_data = {"invalid_key": "invalid_value"}

    # Act + Assert: Ensure a ValidationError is raised
    with pytest.raises(ValidationError):
        await metric_set_tree_service.create_metric_set_tree(metric_set_tree_example)
