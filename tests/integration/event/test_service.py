import pytest
from app.components.events.models.event import EventModel
from app.components.events.service import EventService
from matter_exceptions.exceptions.fastapi import ServerError


# Integration test for creating an event
@pytest.mark.asyncio
async def test_create_event_integration(event_service: EventService, event_example: EventModel):
    # Act: Create an event
    created_event = await event_service.create_event(event_example)

    # Assert: Check that the event returned by the service matches the input
    assert created_event.node_id == event_example.node_id
    assert created_event.event_type == event_example.event_type

    # Assert: Fetch the event from the database to confirm it exists
    fetched_event = await event_service.get_event(created_event.id)
    assert fetched_event is not None
    assert fetched_event.id == created_event.id


# Integration test for retrieving an event by ID
@pytest.mark.asyncio
async def test_get_event_integration(event_service: EventService, event_example: EventModel):
    # Arrange: Create an event
    created_event = await event_service.create_event(event_example)

    # Act: Retrieve the event
    fetched_event = await event_service.get_event(created_event.id)

    # Assert: The fetched event matches the created event
    assert fetched_event.id == created_event.id
    assert fetched_event.event_type == created_event.event_type


# Integration test for deleting an event (soft delete)
@pytest.mark.asyncio
async def test_delete_event_integration(event_service: EventService, event_example: EventModel):
    # Arrange: Create an event
    created_event = await event_service.create_event(event_example)

    # Act: Soft delete the event
    deleted_event = await event_service.delete_event(created_event.id)

    # Assert: Check the event is marked as deleted
    assert deleted_event.deleted is not None

    # Assert: Verify it is still fetchable but marked as deleted
    fetched_event = await event_service.get_event(created_event.id)
    assert fetched_event.deleted is not None


# Integration test for finding events (non-empty result)
@pytest.mark.asyncio
async def test_find_events_non_empty_integration(event_service: EventService, event_example: EventModel):
    # Act: Create a new event
    await event_service.create_event(event_example)

    # Act: Fetch all events
    events = await event_service.find_events()

    # Assert: The result should include the created event
    assert len(events) > 0
    assert any(event.event_type == event_example.event_type for event in events)


# Integration test for finding events (empty result)
@pytest.mark.asyncio
async def test_find_events_empty_integration(event_service: EventService):
    # Act: Fetch all events when there are none
    events = await event_service.find_events()

    # Assert: The result should be empty
    assert len(events) == 0


# Integration test for handling database errors during event creation
@pytest.mark.asyncio
async def test_create_event_database_error_integration(event_service: EventService, event_example: EventModel, mocker):
    # Arrange: Simulate a database error
    mocker.patch.object(event_service._dal, "create_event", side_effect=ServerError("Database error"))

    # Act + Assert: Ensure a ServerError is raised
    with pytest.raises(ServerError):
        await event_service.create_event(event_example)
