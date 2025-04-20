from pydantic import BaseModel
from datetime import date, datetime


class WeeklyPlanBase(BaseModel):
    week_start: date


class WeeklyPlanCreate(WeeklyPlanBase):
    pass


class WeeklyPlanRead(WeeklyPlanBase):
    id: int
    user_id: int
    events_synced: bool
    created_at: datetime

    class Config:
        orm_mode = True
