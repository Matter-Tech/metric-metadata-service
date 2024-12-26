from datetime import datetime, timezone
from uuid import uuid4

import pytest
from app.components.data_metrics.dtos import (
    DataMetricDeletionOutDTO,
    DataMetricInDTO,
    DataMetricListOutDTO,
    DataMetricUpdateInDTO,
    FullDataMetricOutDTO,
)
from pydantic import ValidationError


def get_valid_data_metric_data():
    return {
        "dataId": uuid4(),
        "metricType": "ValidMetricType",
        "name": "ValidDataMetric",
        "metaData": {"key": "value"},
    }


# Tests for DataMetricInDTO
def test_data_metric_in_dto_valid():
    data = get_valid_data_metric_data()
    dto = DataMetricInDTO(**data)
    assert dto.data_id
    assert dto.metric_type == "ValidMetricType"
    assert dto.name == "ValidDataMetric"
    assert dto.meta_data == {"key": "value"}


def test_data_metric_in_dto_invalid_name_too_long():
    data = get_valid_data_metric_data()
    data["name"] = "A" * 101  # Exceeds max length
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        DataMetricInDTO(**data)


def test_data_metric_in_dto_invalid_metric_type_too_long():
    data = get_valid_data_metric_data()
    data["metricType"] = "A" * 51  # Exceeds max length
    with pytest.raises(ValidationError, match="String should have at most 50 characters"):
        DataMetricInDTO(**data)


# Tests for DataMetricUpdateInDTO
def test_data_metric_update_in_dto_valid_partial_update():
    data = {
        "dataId": None,
        "metricType": "UpdatedMetricType",
        "name": "UpdatedDataMetric",
        "metaData": {"newKey": "newValue"},
    }
    dto = DataMetricUpdateInDTO(**data)
    assert dto.metric_type == "UpdatedMetricType"
    assert dto.name == "UpdatedDataMetric"
    assert dto.meta_data == {"newKey": "newValue"}


def test_data_metric_update_in_dto_invalid_name_too_long():
    data = {"name": "A" * 101}
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        DataMetricUpdateInDTO(**data)


# Tests for FullDataMetricOutDTO
def test_full_data_metric_out_dto_valid():
    data = {
        "id": uuid4(),
        "dataId": uuid4(),
        "metricType": "ValidMetricType",
        "name": "ValidDataMetric",
        "metaData": {"key": "value"},
    }
    dto = FullDataMetricOutDTO(**data)
    assert dto.id
    assert dto.data_id
    assert dto.metric_type == "ValidMetricType"
    assert dto.name == "ValidDataMetric"
    assert dto.meta_data == {"key": "value"}


# Tests for DataMetricDeletionOutDTO
def test_data_metric_deletion_out_dto_valid():
    data = {"id": uuid4(), "deletedAt": datetime.now(tz=timezone.utc)}
    dto = DataMetricDeletionOutDTO(**data)
    assert dto.id
    assert dto.deleted_at


# Tests for DataMetricListOutDTO
def test_data_metric_list_out_dto_valid():
    data = {
        "count": 2,
        "data_metrics": [
            {
                "id": uuid4(),
                "dataId": uuid4(),
                "metricType": "MetricType1",
                "name": "DataMetric1",
                "metaData": {"key": "value1"},
            },
            {
                "id": uuid4(),
                "dataId": uuid4(),
                "metricType": "MetricType2",
                "name": "DataMetric2",
                "metaData": {"key": "value2"},
            },
        ],
    }
    dto = DataMetricListOutDTO(**data)
    assert dto.count == 2
    assert len(dto.data_metrics) == 2
    assert dto.data_metrics[0].metric_type == "MetricType1"
    assert dto.data_metrics[1].meta_data == {"key": "value2"}
