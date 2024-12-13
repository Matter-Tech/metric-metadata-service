from datetime import datetime, timezone
from uuid import uuid4

import pytest
from app.common.enums.enums import PlacementEnum, StatusEnum
from app.components.metric_sets.dtos import (
    FullMetricSetOutDTO,
    MetricSetDeletionOutDTO,
    MetricSetInDTO,
    MetricSetListOutDTO,
    MetricSetUpdateInDTO,
)
from pydantic import ValidationError


def get_valid_metric_set_data():
    return {
        "status": StatusEnum.DEPLOYED,
        "shortName": "ValidShortName",
        "placement": PlacementEnum.SDGS,
        "metaData": {"key": "value"},
    }


# Tests for MetricSetInDTO
def test_metric_set_in_dto_valid():
    data = get_valid_metric_set_data()
    dto = MetricSetInDTO(**data)
    assert dto.status == StatusEnum.DEPLOYED
    assert dto.short_name == "ValidShortName"
    assert dto.placement == PlacementEnum.SDGS
    assert dto.meta_data == {"key": "value"}


def test_metric_set_in_dto_invalid_short_name_too_long():
    data = get_valid_metric_set_data()
    data["shortName"] = "A" * 101  # Exceeds max length
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        MetricSetInDTO(**data)


def test_metric_set_in_dto_invalid_status():
    data = get_valid_metric_set_data()
    data["status"] = "INVALID_STATUS"  # Invalid status value
    with pytest.raises(ValidationError, match="Input should be"):
        MetricSetInDTO(**data)


# Tests for MetricSetUpdateInDTO
def test_metric_set_update_in_dto_valid_partial_update():
    data = {
        "status": None,
        "shortName": "UpdatedShortName",
        "placement": None,
        "metaData": {"newKey": "newValue"},
    }
    dto = MetricSetUpdateInDTO(**data)
    assert dto.status is None
    assert dto.short_name == "UpdatedShortName"
    assert dto.placement is None
    assert dto.meta_data == {"newKey": "newValue"}


def test_metric_set_update_in_dto_invalid_short_name_too_long():
    data = {"shortName": "A" * 101}
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        MetricSetUpdateInDTO(**data)


def test_metric_set_update_in_dto_invalid_status():
    data = {"status": "INVALID_STATUS"}
    with pytest.raises(ValidationError, match="Input should be"):
        MetricSetUpdateInDTO(**data)


# Tests for FullMetricSetOutDTO
def test_full_metric_set_out_dto_valid():
    data = {
        "id": uuid4(),
        "status": StatusEnum.DEPLOYED,
        "shortName": "ValidShortName",
        "placement": PlacementEnum.SDGS,
        "metaData": {"key": "value"},
    }
    dto = FullMetricSetOutDTO(**data)
    assert dto.id
    assert dto.status == StatusEnum.DEPLOYED
    assert dto.short_name == "ValidShortName"
    assert dto.placement == PlacementEnum.SDGS
    assert dto.meta_data == {"key": "value"}


# Tests for MetricSetDeletionOutDTO
def test_metric_set_deletion_out_dto_valid():
    data = {"id": uuid4(), "deletedAt": datetime.now(tz=timezone.utc)}
    dto = MetricSetDeletionOutDTO(**data)
    assert dto.id
    assert dto.deleted_at


# Tests for MetricSetListOutDTO
def test_metric_set_list_out_dto_valid():
    data = {
        "count": 2,
        "metric_sets": [
            {
                "id": uuid4(),
                "status": StatusEnum.DEPLOYED,
                "shortName": "ShortName1",
                "placement": PlacementEnum.SDGS,
                "metaData": {"key": "value1"},
            },
            {
                "id": uuid4(),
                "status": StatusEnum.DEPLOYED,
                "shortName": "ShortName2",
                "placement": PlacementEnum.SDGS,
                "metaData": {"key": "value2"},
            },
        ],
    }
    dto = MetricSetListOutDTO(**data)
    assert dto.count == 2
    assert len(dto.metric_sets) == 2
    assert dto.metric_sets[0].short_name == "ShortName1"
    assert dto.metric_sets[1].placement == PlacementEnum.SDGS
