from datetime import datetime, timezone
from uuid import uuid4

import pytest
from app.common.enums.enums import NodeTypeEnum
from app.components.metric_set_trees.dtos import (
    FullMetricSetTreeOutDTO,
    MetricSetTreeDeletionOutDTO,
    MetricSetTreeInDTO,
    MetricSetTreeListOutDTO,
    MetricSetTreeUpdateInDTO,
)
from pydantic import ValidationError


def get_valid_metric_set_tree_data():
    return {
        "metricSetId": uuid4(),
        "nodeType": NodeTypeEnum.METRIC,
        "nodeDepth": 1,
        "nodeName": "ValidNode",
        "nodeDescription": "A valid description",
        "nodeReferenceId": "ref123",
        "nodeSpecial": "specialValue",
        "metaData": {"key": "value"},
    }


# Tests for MetricSetTreeInDTO
def test_metric_set_tree_in_dto_valid():
    data = get_valid_metric_set_tree_data()
    dto = MetricSetTreeInDTO(**data)
    assert dto.metric_set_id
    assert dto.node_type == NodeTypeEnum.METRIC
    assert dto.node_depth == 1
    assert dto.node_name == "ValidNode"
    assert dto.node_description == "A valid description"
    assert dto.node_reference_id == "ref123"
    assert dto.node_special == "specialValue"
    assert dto.meta_data == {"key": "value"}


def test_metric_set_tree_in_dto_invalid_node_depth():
    data = get_valid_metric_set_tree_data()
    data["nodeDepth"] = -1  # Invalid depth
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        MetricSetTreeInDTO(**data)


# Tests for MetricSetTreeUpdateInDTO
def test_metric_set_tree_update_in_dto_valid_partial_update():
    data = {
        "metricSetId": None,
        "nodeType": NodeTypeEnum.METRIC,
        "nodeDepth": None,
        "nodeName": "UpdatedNode",
        "nodeDescription": "Updated description",
        "nodeReferenceId": None,
        "nodeSpecial": None,
        "metaData": None,
    }
    dto = MetricSetTreeUpdateInDTO(**data)
    assert dto.metric_set_id is None
    assert dto.node_type == NodeTypeEnum.METRIC
    assert dto.node_depth is None
    assert dto.node_name == "UpdatedNode"
    assert dto.node_description == "Updated description"
    assert dto.node_reference_id is None
    assert dto.node_special is None
    assert dto.meta_data is None


def test_metric_set_tree_update_in_dto_invalid_meta_data():
    data = {"metaData": "Invalid string instead of dict"}
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        MetricSetTreeUpdateInDTO(**data)


# Tests for FullMetricSetTreeOutDTO
def test_full_metric_set_tree_out_dto_valid():
    data = {
        "id": uuid4(),
        "metricSetId": uuid4(),
        "nodeType": NodeTypeEnum.METRIC,
        "nodeDepth": 1,
        "nodeName": "ValidNode",
        "nodeDescription": "Valid description",
        "nodeReferenceId": "ref123",
        "nodeSpecial": "specialValue",
        "metaData": {"key": "value"},
    }
    dto = FullMetricSetTreeOutDTO(**data)
    assert dto.id
    assert dto.metric_set_id
    assert dto.node_type == NodeTypeEnum.METRIC
    assert dto.node_depth == 1
    assert dto.node_name == "ValidNode"
    assert dto.node_description == "Valid description"
    assert dto.node_reference_id == "ref123"
    assert dto.node_special == "specialValue"
    assert dto.meta_data == {"key": "value"}


# Tests for MetricSetTreeDeletionOutDTO
def test_metric_set_tree_deletion_out_dto_valid():
    data = {"id": uuid4(), "deletedAt": datetime.now(tz=timezone.utc)}
    dto = MetricSetTreeDeletionOutDTO(**data)
    assert dto.id
    assert dto.deleted_at


# Tests for MetricSetTreeListOutDTO
def test_metric_set_tree_list_out_dto_valid():
    data = {
        "count": 2,
        "metric_set_trees": [
            {
                "id": uuid4(),
                "metricSetId": uuid4(),
                "nodeType": NodeTypeEnum.METRIC,
                "nodeDepth": 1,
                "nodeName": "ValidNode1",
                "nodeDescription": "Description 1",
                "nodeReferenceId": "ref1",
                "nodeSpecial": "specialValue1",
                "metaData": {"key": "value1"},
            },
            {
                "id": uuid4(),
                "metricSetId": uuid4(),
                "nodeType": NodeTypeEnum.METRIC,
                "nodeDepth": 2,
                "nodeName": "ValidNode2",
                "nodeDescription": "Description 2",
                "nodeReferenceId": "ref2",
                "nodeSpecial": "specialValue2",
                "metaData": {"key": "value2"},
            },
        ],
    }
    dto = MetricSetTreeListOutDTO(**data)
    assert dto.count == 2
    assert len(dto.metric_set_trees) == 2
    assert dto.metric_set_trees[0].node_name == "ValidNode1"
    assert dto.metric_set_trees[1].node_type == NodeTypeEnum.METRIC
