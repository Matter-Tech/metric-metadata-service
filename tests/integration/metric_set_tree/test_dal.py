from uuid import uuid4

import pytest
from app.components.metric_set_trees.dal import MetricSetTreeDAL
from app.components.metric_set_trees.models.metric_set_tree import MetricSetTreeModel
from app.components.metric_set_trees.models.metric_set_trees_update import MetricSetTreeUpdateModel
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError


# Integration test for creating a metric set tree
@pytest.mark.asyncio
async def test_create_metric_set_tree_integration(
    metric_set_tree_dal: MetricSetTreeDAL, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id
    # Act: Create the metric set tree using the DAL
    created_metric_set_tree = await metric_set_tree_dal.create_metric_set_tree(metric_set_tree_example)

    # Assert: Check the created metric set tree's data
    assert created_metric_set_tree.node_name == metric_set_tree_example.node_name
    assert created_metric_set_tree.node_description == metric_set_tree_example.node_description

    # Assert: Verify the metric set tree exists in the database
    fetched_metric_set_tree = await metric_set_tree_dal.get_metric_set_tree(created_metric_set_tree.id)
    assert fetched_metric_set_tree is not None
    assert fetched_metric_set_tree.id == created_metric_set_tree.id
    assert fetched_metric_set_tree.node_name == created_metric_set_tree.node_name


# Integration test for getting a metric set tree by ID
@pytest.mark.asyncio
async def test_get_metric_set_tree_integration(
    metric_set_tree_dal: MetricSetTreeDAL, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id
    # Act: Create the metric set tree
    created_metric_set_tree = await metric_set_tree_dal.create_metric_set_tree(metric_set_tree_example)

    # Act: Fetch the metric set tree by ID
    fetched_metric_set_tree = await metric_set_tree_dal.get_metric_set_tree(created_metric_set_tree.id)

    # Assert: Verify the fetched data matches the created data
    assert fetched_metric_set_tree.id == created_metric_set_tree.id
    assert fetched_metric_set_tree.node_name == created_metric_set_tree.node_name
    assert fetched_metric_set_tree.node_description == created_metric_set_tree.node_description


# Integration test for getting a non-existent metric set tree
@pytest.mark.asyncio
async def test_get_metric_set_tree_not_found_integration(metric_set_tree_dal: MetricSetTreeDAL):
    # Act & Assert: Ensure fetching a non-existent metric set tree raises an error
    with pytest.raises(DatabaseRecordNotFoundError):
        await metric_set_tree_dal.get_metric_set_tree(uuid4())  # Random UUID


# Integration test for finding metric set trees (non-empty result)
@pytest.mark.asyncio
async def test_find_metric_set_trees_non_empty_integration(
    metric_set_tree_dal: MetricSetTreeDAL, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id

    # Act: Create a metric set tree
    await metric_set_tree_dal.create_metric_set_tree(metric_set_tree_example)

    # Act: Find metric set trees
    metric_set_trees = await metric_set_tree_dal.find_metric_set_trees()

    # Assert: Verify the result contains at least one metric set tree
    assert len(metric_set_trees) > 0
    assert metric_set_trees[0].node_name == metric_set_tree_example.node_name


# Integration test for finding metric set trees (empty result)
@pytest.mark.asyncio
async def test_find_metric_set_trees_empty_integration(metric_set_tree_dal: MetricSetTreeDAL):
    # Act: Find metric set trees with an empty database
    metric_set_trees = await metric_set_tree_dal.find_metric_set_trees()

    # Assert: The result should be an empty list
    assert len(metric_set_trees) == 0


# Integration test for updating a metric set tree
@pytest.mark.asyncio
async def test_update_metric_set_tree_integration(
    metric_set_tree_dal: MetricSetTreeDAL, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id
    # Act: Create the metric set tree
    created_metric_set_tree = await metric_set_tree_dal.create_metric_set_tree(metric_set_tree_example)

    # Act: Update the metric set tree
    updated_metric_set_tree = await metric_set_tree_dal.update_metric_set_tree(
        created_metric_set_tree.id,
        MetricSetTreeUpdateModel(node_name="Updated Metric Set Tree"),
    )

    # Assert: Verify the metric set tree was updated correctly
    assert updated_metric_set_tree.node_name == "Updated Metric Set Tree"
    assert updated_metric_set_tree.id == created_metric_set_tree.id

    # Assert: Fetch and verify the updates
    fetched_metric_set_tree = await metric_set_tree_dal.get_metric_set_tree(created_metric_set_tree.id)
    assert fetched_metric_set_tree.node_name == "Updated Metric Set Tree"


# Integration test for deleting a metric set tree (soft delete)
@pytest.mark.asyncio
async def test_delete_metric_set_tree_soft_integration(
    metric_set_tree_dal: MetricSetTreeDAL, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id
    # Act: Create the metric set tree
    created_metric_set_tree = await metric_set_tree_dal.create_metric_set_tree(metric_set_tree_example)

    # Act: Soft delete the metric set tree
    deleted_metric_set_tree = await metric_set_tree_dal.delete_metric_set_tree(created_metric_set_tree.id)

    # Assert: Verify the metric set tree is soft-deleted
    assert deleted_metric_set_tree.deleted is not None
    assert deleted_metric_set_tree.id == created_metric_set_tree.id

    # Assert: Fetch the soft-deleted metric set tree
    fetched_metric_set_tree = await metric_set_tree_dal.get_metric_set_tree(created_metric_set_tree.id)
    assert fetched_metric_set_tree.deleted is not None


# Integration test for deleting a metric set tree (permanent delete)
@pytest.mark.asyncio
async def test_delete_metric_set_tree_permanent_integration(
    metric_set_tree_dal: MetricSetTreeDAL, metric_set_tree_example: MetricSetTreeModel, metric_set_test_entry
):
    metric_set = await metric_set_test_entry
    metric_set_tree_example.metric_set_id = metric_set.id
    # Act: Create the metric set tree
    created_metric_set_tree = await metric_set_tree_dal.create_metric_set_tree(metric_set_tree_example)

    # Act: Permanently delete the metric set tree
    await metric_set_tree_dal.delete_metric_set_tree(created_metric_set_tree.id, soft_delete=False)

    # Assert: Verify the metric set tree no longer exists
    with pytest.raises(DatabaseRecordNotFoundError):
        await metric_set_tree_dal.get_metric_set_tree(created_metric_set_tree.id)
