import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy import select, text

from routes.bets import Bet, BetResponse
from routes.events import Event, EventStatuses


@pytest_asyncio.fixture(scope="function")
async def setup_bets(db_session):
    event_data = [
        {"name": "Event 1", "status": EventStatuses.PENDING},
        {"name": "Event 2", "status": EventStatuses.WIN}
    ]
    async with db_session as session:
        events_ids = []
        for data in event_data:
            event = Event(**data)
            session.add(event)
            await session.commit()
            await session.refresh(event)
            events_ids.append(event.id)

        bet_data = [
            {"event_id": events_ids[0], "amount": Decimal('10.00')},
            {"event_id": events_ids[1], "amount": Decimal('20.00')}
        ]
        for data in bet_data:
            bet = Bet(**data)
            session.add(bet)
        await session.commit()
    yield
    async with db_session as session:
        await session.execute(text("DELETE FROM bets"))
        await session.execute(text("DELETE FROM events"))
        await session.commit()


@pytest.mark.asyncio
class TestBetEndpoints:

    async def test_get_bets(self, test_client, setup_bets):
        response = test_client.get("/bets/")
        assert response.status_code == 200
        bets = response.json()
        assert len(bets) == 2
        for bet in bets:
            assert "id" in bet
            assert "event_id" in bet
            assert "status" in bet
            assert "amount" in bet

    @pytest.mark.parametrize("amount", [30.0, 40.0])
    async def test_create_bet(self, test_client, db_session, amount):
        async with db_session as session:
            event_ids = await session.scalars(select(Event.id))
            event_ids = event_ids.all()
        for event_id in event_ids:
            bet_data = {"event_id": event_id, "amount": amount}
            response = test_client.post("/bets/", json=bet_data)
            assert response.status_code == 200
            created_bet = BetResponse(**response.json())
            assert created_bet.event_id == bet_data["event_id"]
            assert created_bet.amount == Decimal(str(bet_data["amount"]))
