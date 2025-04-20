from pydantic import BaseModel
from datetime import date, datetime


class LogEntryBase(BaseModel):
    date: date
    calories_in: int
    calories_out: int


class LogEntryCreate(LogEntryBase):
    pass


class LogEntryRead(LogEntryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
