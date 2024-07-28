from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.models import Event, EventStatuses
from database.postgres import Database

router = APIRouter(prefix='/events', tags=['events'])


class EventStatus(BaseModel):
    status: str

    @field_validator('status')
    def validate_status(v: str) -> str:
        if v not in EventStatuses.__members__:
            raise ValueError('Invalid status, must be one of: ' + ', '.join(EventStatuses.__members__))
        return v


class BaseEvent(EventStatus):
    name: str


class EventResponse(BaseEvent):
    id: int = Field(gt=0)


class UpdateEvent(EventStatus):
    pass


@router.get('/', response_model=list[EventResponse])
async def get_events(db: Database = Depends(Database.get_instance)):
    resp = []
    async with db.get_session() as session:
        for event in await session.scalars(select(Event)):
            resp.append(EventResponse(
                id=event.id,
                name=event.name,
                status=event.status.value
            ))
    return resp


@router.post('/', response_model=EventResponse)
async def create_event(event: BaseEvent, db: Database = Depends(Database.get_instance)):
    async with db.get_session() as session:
        new_event = Event(**event.model_dump())
        session.add(new_event)
        try:
            await session.commit()
            await session.refresh(new_event)
            return EventResponse(
                id=new_event.id,
                name=new_event.name,
                status=new_event.status.value
            )
        except IntegrityError:
            raise HTTPException(status_code=400, detail='Event already exists')


@router.put('/{event_id}', response_model=EventResponse)
async def update_event(event_id: int, event_status: UpdateEvent, db: Database = Depends(Database.get_instance)):
    async with db.get_session() as session:
        event = await session.get(Event, event_id)
        if event is None:
            raise HTTPException(status_code=404, detail='Event not found')
        event.status = EventStatuses[event_status.status]
        await session.commit()
        await session.refresh(event)
        return EventResponse(
            id=event.id,
            name=event.name,
            status=event.status.value
        )
