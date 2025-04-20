# app/schemas/goal.py
from pydantic import BaseModel
from datetime import date, datetime


class GoalCreate(BaseModel):
    description: str
    start_date: date


class GoalRead(BaseModel):
    id: int
    user_id: int
    description: str
    start_date: date
    created_at: datetime

    class Config:
        orm_mode = True
