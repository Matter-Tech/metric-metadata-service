from datetime import datetime, timezone
from uuid import uuid4

import pytest
from app.common.enums.enums import EntityTypeEnum, EventTypeEnum
from app.components.events.dtos import (
    EventDeletionOutDTO,
    EventFilterInDTO,
    EventListOutDTO,
    FullEventOutDTO,
)
from pydantic import ValidationError


def get_valid_event_data():
    return {
        "eventType": EventTypeEnum.CREATED,
        "entityType": EntityTypeEnum.METRIC_SET,
        "nodeId": uuid4(),
        "userId": uuid4(),
    }


# Tests for EventFilterInDTO
def test_event_filter_in_dto_valid():
    data = get_valid_event_data()
    dto = EventFilterInDTO(**data)
    assert dto.event_type == EventTypeEnum.CREATED
    assert dto.entity_type == EntityTypeEnum.METRIC_SET
    assert dto.node_id
    assert dto.user_id


def test_event_filter_in_dto_invalid_status():
    data = get_valid_event_data()
    data["eventType"] = "INVALID_EVENT_TYPE"  # Invalid EventType
    with pytest.raises(ValidationError, match="Input should be"):
        EventFilterInDTO(**data)


# Tests for FullEventOutDTO
def test_full_event_out_dto_valid():
    data = {
        "id": uuid4(),
        "eventType": EventTypeEnum.UPDATED,
        "entityType": EntityTypeEnum.METRIC,
        "nodeId": uuid4(),
        "userId": uuid4(),
        "timestamp": datetime.now(tz=timezone.utc),
        "newData": {"key": "value"},
    }
    dto = FullEventOutDTO(**data)
    assert dto.id
    assert dto.event_type == EventTypeEnum.UPDATED
    assert dto.entity_type == EntityTypeEnum.METRIC
    assert dto.node_id
    assert dto.user_id
    assert dto.created
    assert dto.new_data == {"key": "value"}


# Tests for EventDeletionOutDTO
def test_event_deletion_out_dto_valid():
    data = {"id": uuid4(), "deletedAt": datetime.now(tz=timezone.utc)}
    dto = EventDeletionOutDTO(**data)
    assert dto.id
    assert dto.deleted_at


# Tests for EventListOutDTO
def test_event_list_out_dto_valid():
    data = {
        "count": 2,
        "events": [
            {
                "id": uuid4(),
                "eventType": EventTypeEnum.DELETED,
                "entityType": EntityTypeEnum.METRIC_SET,
                "nodeId": uuid4(),
                "userId": uuid4(),
                "timestamp": datetime.now(tz=timezone.utc),
                "newData": {"key": "value1"},
            },
            {
                "id": uuid4(),
                "eventType": EventTypeEnum.DELETED,
                "entityType": EntityTypeEnum.METRIC,
                "nodeId": uuid4(),
                "userId": uuid4(),
                "timestamp": datetime.now(tz=timezone.utc),
                "newData": {"key": "value2"},
            },
        ],
    }
    dto = EventListOutDTO(**data)
    assert dto.count == 2
    assert len(dto.events) == 2
    assert dto.events[0].event_type == EventTypeEnum.DELETED
    assert dto.events[1].entity_type == EntityTypeEnum.METRIC
