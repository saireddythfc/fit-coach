from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    events_synced = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="weekly_plans")
