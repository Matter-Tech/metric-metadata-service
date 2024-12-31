from uuid import uuid4

import pytest
from app.components.events.dal import EventDAL
from app.components.events.models.event import EventModel
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError


# Integration test for creating an event
@pytest.mark.asyncio
async def test_create_event_integration(event_dal: EventDAL, event_example: EventModel):
    # Act: Create the event using the DAL
    created_event = await event_dal.create_event(event_example)

    # Assert: Check the created event's data
    assert created_event.event_type == event_example.event_type
    assert created_event.user_id == event_example.user_id

    # Assert: Verify the event exists in the database
    fetched_event = await event_dal.get_event(created_event.id)
    assert fetched_event is not None
    assert fetched_event.id == created_event.id
    assert fetched_event.entity_type == created_event.entity_type


# Integration test for getting an event by ID
@pytest.mark.asyncio
async def test_get_event_integration(event_dal: EventDAL, event_example: EventModel):
    # Act: Create the event
    created_event = await event_dal.create_event(event_example)

    # Act: Fetch the event by ID
    fetched_event = await event_dal.get_event(created_event.id)

    # Assert: Verify the fetched data matches the created data
    assert fetched_event.id == created_event.id
    assert fetched_event.user_id == created_event.user_id
    assert fetched_event.entity_type == created_event.entity_type


# Integration test for getting a non-existent event
@pytest.mark.asyncio
async def test_get_event_not_found_integration(event_dal: EventDAL):
    # Act & Assert: Ensure fetching a non-existent event raises an error
    with pytest.raises(DatabaseRecordNotFoundError):
        await event_dal.get_event(uuid4())  # Random UUID


# Integration test for finding events (non-empty result)
@pytest.mark.asyncio
async def test_find_events_non_empty_integration(event_dal: EventDAL, event_example: EventModel):
    # Act: Create an event
    await event_dal.create_event(event_example)

    # Act: Find events
    events = await event_dal.find_events()

    # Assert: Verify the result contains at least one event
    assert len(events) > 0
    assert events[0].user_id == event_example.user_id


# Integration test for finding events (empty result)
@pytest.mark.asyncio
async def test_find_events_empty_integration(event_dal: EventDAL):
    # Act: Find events with an empty database
    events = await event_dal.find_events()

    # Assert: The result should be an empty list
    assert len(events) == 0


# Integration test for deleting an event (soft delete)
@pytest.mark.asyncio
async def test_delete_event_soft_integration(event_dal: EventDAL, event_example: EventModel):
    # Act: Create the event
    created_event = await event_dal.create_event(event_example)

    # Act: Soft delete the event
    deleted_event = await event_dal.delete_event(created_event.id)

    # Assert: Verify the event is soft-deleted
    assert deleted_event.deleted is not None
    assert deleted_event.id == created_event.id

    # Assert: Fetch the soft-deleted event
    fetched_event = await event_dal.get_event(created_event.id)
    assert fetched_event.deleted is not None


# Integration test for deleting an event (permanent delete)
@pytest.mark.asyncio
async def test_delete_event_permanent_integration(event_dal: EventDAL, event_example: EventModel):
    # Act: Create the event
    created_event = await event_dal.create_event(event_example)

    # Act: Permanently delete the event
    await event_dal.delete_event(created_event.id, soft_delete=False)

    # Assert: Verify the event no longer exists
    with pytest.raises(DatabaseRecordNotFoundError):
        await event_dal.get_event(created_event.id)
