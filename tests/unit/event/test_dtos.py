from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.common.enums.enums import EventTypeEnum, EntityTypeEnum
from app.components.events.dtos import EventDeletionOutDTO, FullEventOutDTO, EventListOutDTO, EventFilterInDTO


# Utility: Generate a valid UUID
def generate_uuid():
    return uuid4()

# Utility: Sample valid data
def get_valid_event_data():
    return {
        "id": generate_uuid(),
        "eventType": EventTypeEnum.CREATED,
        "entityType": EntityTypeEnum.METRIC,
        "nodeId": generate_uuid(),
        "userId": generate_uuid(),
        "timestamp": datetime.now(tz=timezone.utc),
        "newData": {"key": "value"},
    }

# Tests for EventFilterInDTO
def test_event_filter_in_dto_valid():
    data = {
        "eventType": EventTypeEnum.CREATED,
        "entityType": EntityTypeEnum.METRIC,
        "nodeId": generate_uuid(),
        "userId": generate_uuid(),
    }
    dto = EventFilterInDTO(**data)
    assert dto.event_type == EventTypeEnum.CREATED
    assert dto.entity_type == EntityTypeEnum.METRIC
    assert dto.node_id is not None
    assert dto.user_id is not None

def test_event_filter_in_dto_invalid_node_id():
    data = {
        "eventType": EventTypeEnum.CREATED,
        "entityType": EntityTypeEnum.METRIC,
        "nodeId": "invalid-uuid",
        "userId": generate_uuid(),
    }
    with pytest.raises(ValidationError, match="Input should be a valid UUID"):
        EventFilterInDTO(**data)

def test_event_filter_in_dto_missing_fields():
    data = {}
    dto = EventFilterInDTO(**data)
    assert dto.event_type is None
    assert dto.entity_type is None
    assert dto.node_id is None
    assert dto.user_id is None

# Tests for FullEventOutDTO
def test_full_event_out_dto_valid():
    data = get_valid_event_data()
    dto = FullEventOutDTO(**data)
    assert dto.id == data["id"]
    assert dto.event_type == EventTypeEnum.CREATED
    assert dto.entity_type == EntityTypeEnum.METRIC
    assert dto.node_id == data["nodeId"]
    assert dto.user_id == data["userId"]
    assert dto.created == data["timestamp"]
    assert dto.new_data == {"key": "value"}

def test_full_event_out_dto_invalid_new_data():
    data = get_valid_event_data()
    data["newData"] = "invalid-data"
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        FullEventOutDTO(**data)

# Tests for EventDeletionOutDTO
def test_event_deletion_out_dto_valid():
    data = {
        "id": generate_uuid(),
        "deletedAt": datetime.now(tz=timezone.utc),
    }
    dto = EventDeletionOutDTO(**data)
    assert dto.id == data["id"]
    assert dto.deleted_at == data["deletedAt"]

def test_event_deletion_out_dto_default_deleted_at():
    data = {"id": generate_uuid()}
    dto = EventDeletionOutDTO(**data)
    assert dto.deleted_at is not None
    assert isinstance(dto.deleted_at, datetime)

# Tests for EventListOutDTO
def test_event_list_out_dto_valid():
    events = [get_valid_event_data() for _ in range(2)]
    data = {
        "count": 2,
        "events": [FullEventOutDTO(**event) for event in events],
    }
    dto = EventListOutDTO(**data)
    assert dto.count == 2
    assert len(dto.events) == 2
    assert dto.events[0].event_type == EventTypeEnum.CREATED

def test_event_list_out_dto_invalid_events():
    data = {
        "count": 2,
        "events": ["invalid-event"],
    }
    with pytest.raises(ValidationError, match="dictionary or instance of FullEventOutDTO"):
        EventListOutDTO(**data)