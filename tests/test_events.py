import datetime

import pytest
import pytest_asyncio
import sqlalchemy
from sqlalchemy import select

from routes.events import Event, EventStatuses, EventResponse


@pytest_asyncio.fixture(scope="function")
async def setup_events(db_session):
    event_data = [
        {"name": "Event 1", "status": EventStatuses.PENDING, "updated_at": datetime.datetime.now(),
         "created_at": datetime.datetime.now()},
        {"name": "Event 2", "status": EventStatuses.WIN, "updated_at": datetime.datetime.now(),
         "created_at": datetime.datetime.now()},
    ]
    async with db_session as session:
        for data in event_data:
            event = Event(**data)
            session.add(event)
        await session.commit()
    yield
    async with db_session as session:
        await session.execute(sqlalchemy.text("DELETE FROM events"))
        await session.commit()


@pytest.mark.asyncio
class TestEventEndpoints:

    async def test_get_events(self, test_client, setup_events):
        response = test_client.get("/events/")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 2
        for event in events:
            assert "id" in event
            assert "name" in event
            assert "status" in event

    @pytest.mark.parametrize("event_data", [
        {"name": "Event 3", "status": "PENDING"},
        {"name": "Event 4", "status": "WIN"}
    ])
    async def test_create_event(self, test_client, event_data):
        response = test_client.post("/events/", json=event_data)
        assert response.status_code == 200
        created_event = EventResponse(**response.json())
        assert created_event.name == event_data["name"]
        assert created_event.status == event_data["status"]

    async def test_update_event(self, test_client, db_session, setup_events):
        async with db_session as session:
            event = await session.scalar(select(Event).limit(1))
        response = test_client.put(f"/events/{event.id}", json={"status": "LOSE"})
        assert response.status_code == 200
        updated_event = EventResponse(**response.json())
        assert updated_event.id == event.id
        assert updated_event.status == "LOSE"
