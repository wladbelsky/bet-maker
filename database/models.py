from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Double, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class EventStatuses(PyEnum):
    PENDING = 'PENDING'
    WIN = 'WIN'
    LOSE = 'LOSE'


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(type_=TIMESTAMP(timezone=True), nullable=False, default=func.now())
    updated_at = Column(type_=TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())
    name = Column(String)
    status = Column(Enum(EventStatuses, name='event_statuses'))


class Bet(Base):
    __tablename__ = 'bets'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created_at = Column(type_=TIMESTAMP(timezone=True), nullable=False, default=func.now())
    updated_at = Column(type_=TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    event = relationship('Event', lazy="selectin")
    amount = Column(Double)
