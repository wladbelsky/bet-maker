from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_serializer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from database.models import Bet
from database.postgres import Database

router = APIRouter(prefix='/bets', tags=['bets'])


class AmountBase(BaseModel):
    amount: Decimal = Field(decimal_places=2, ge=0)

    @field_serializer('amount', when_used='json')
    def serialize_amount(v: Decimal) -> str:
        return format(v, '.2f')


class BetResponse(AmountBase):
    id: int = Field(gt=0)
    event_id: int
    status: str


class BetRequest(AmountBase):
    event_id: int


@router.get('/', response_model=list[BetResponse])
async def get_bets(db: Database = Depends(Database.get_instance)):
    resp = []
    async with db.get_session() as session:
        for bet in await session.scalars(select(Bet).options(joinedload(Bet.event))):
            resp.append(BetResponse(
                id=bet.id,
                event_id=bet.event_id,
                status=bet.event.status.value,
                amount=bet.amount
            ))
    return resp


@router.post('/', response_model=BetResponse, responses={
    400: {'description': 'Event not found',
          'content': {
              "detail": "Event not found"
          }}}
             )
async def create_bet(bet: BetRequest, db: Database = Depends(Database.get_instance)):
    async with db.get_session() as session:
        new_bet = Bet(amount=bet.amount, event_id=bet.event_id)
        session.add(new_bet)
        try:
            await session.commit()
            await session.refresh(new_bet)
            return BetResponse(
                id=new_bet.id,
                event_id=new_bet.event_id,
                status=new_bet.event.status.value,
                amount=new_bet.amount
            )
        except IntegrityError:
            raise HTTPException(status_code=400, detail='Event not found')
