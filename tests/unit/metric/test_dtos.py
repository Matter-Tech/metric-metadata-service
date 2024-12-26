from datetime import datetime, timezone
from uuid import uuid4

import pytest
from app.common.enums.enums import StatusEnum
from app.components.metrics.dtos import (
    FullMetricOutDTO,
    MetricDeletionOutDTO,
    MetricInDTO,
    MetricListOutDTO,
    MetricUpdateInDTO,
)
from pydantic import ValidationError


def get_valid_metric_data():
    return {
        "metricSetId": uuid4(),
        "parentSectionId": uuid4(),
        "parentMetricId": uuid4(),
        "dataMetricId": uuid4(),
        "status": StatusEnum.DEPLOYED,
        "name": "ValidMetric",
        "nameSuffix": "Suffix",
        "metaData": {"key": "value"},
    }


# Tests for MetricInDTO
def test_metric_in_dto_valid():
    data = get_valid_metric_data()
    dto = MetricInDTO(**data)
    assert dto.metric_set_id
    assert dto.status == StatusEnum.DEPLOYED
    assert dto.name == "ValidMetric"
    assert dto.name_suffix == "Suffix"
    assert dto.meta_data == {"key": "value"}


def test_metric_in_dto_invalid_name_too_long():
    data = get_valid_metric_data()
    data["name"] = "A" * 101  # Exceeds max length
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        MetricInDTO(**data)


def test_metric_in_dto_invalid_status():
    data = get_valid_metric_data()
    data["status"] = "INVALID_STATUS"  # Invalid status value
    with pytest.raises(ValidationError, match="Input should be"):
        MetricInDTO(**data)


# Tests for MetricUpdateInDTO
def test_metric_update_in_dto_valid_partial_update():
    data = {
        "metricSetId": None,
        "parentSectionId": None,
        "parentMetricId": None,
        "dataMetricId": None,
        "status": StatusEnum.DEPLOYED,
        "name": "UpdatedMetric",
        "nameSuffix": "UpdatedSuffix",
        "metaData": {"newKey": "newValue"},
    }
    dto = MetricUpdateInDTO(**data)
    assert dto.status == StatusEnum.DEPLOYED
    assert dto.name == "UpdatedMetric"
    assert dto.name_suffix == "UpdatedSuffix"
    assert dto.meta_data == {"newKey": "newValue"}


def test_metric_update_in_dto_invalid_name_too_long():
    data = {"name": "A" * 101}
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        MetricUpdateInDTO(**data)


def test_metric_update_in_dto_invalid_status():
    data = {"status": "INVALID_STATUS"}
    with pytest.raises(ValidationError, match="Input should be"):
        MetricUpdateInDTO(**data)


# Tests for FullMetricOutDTO
def test_full_metric_out_dto_valid():
    data = {
        "id": uuid4(),
        "metricSetId": uuid4(),
        "parentSectionId": uuid4(),
        "parentMetricId": uuid4(),
        "dataMetricId": uuid4(),
        "status": StatusEnum.DEPLOYED,
        "name": "ValidMetric",
        "nameSuffix": "Suffix",
        "metaData": {"key": "value"},
    }
    dto = FullMetricOutDTO(**data)
    assert dto.id
    assert dto.metric_set_id
    assert dto.status == StatusEnum.DEPLOYED
    assert dto.name == "ValidMetric"
    assert dto.name_suffix == "Suffix"
    assert dto.meta_data == {"key": "value"}


# Tests for MetricDeletionOutDTO
def test_metric_deletion_out_dto_valid():
    data = {"id": uuid4(), "deletedAt": datetime.now(tz=timezone.utc)}
    dto = MetricDeletionOutDTO(**data)
    assert dto.id
    assert dto.deleted_at


# Tests for MetricListOutDTO
def test_metric_list_out_dto_valid():
    data = {
        "count": 2,
        "metrics": [
            {
                "id": uuid4(),
                "metricSetId": uuid4(),
                "parentSectionId": uuid4(),
                "parentMetricId": uuid4(),
                "dataMetricId": uuid4(),
                "status": StatusEnum.DEPLOYED,
                "name": "Metric1",
                "nameSuffix": "Suffix1",
                "metaData": {"key": "value1"},
            },
            {
                "id": uuid4(),
                "metricSetId": uuid4(),
                "parentSectionId": uuid4(),
                "parentMetricId": uuid4(),
                "dataMetricId": uuid4(),
                "status": StatusEnum.DEPLOYED,
                "name": "Metric2",
                "nameSuffix": "Suffix2",
                "metaData": {"key": "value2"},
            },
        ],
    }
    dto = MetricListOutDTO(**data)
    assert dto.count == 2
    assert len(dto.metrics) == 2
    assert dto.metrics[0].name == "Metric1"
    assert dto.metrics[1].status == StatusEnum.DEPLOYED
