# models/user.py

from sqlalchemy import Column, Integer, String
from app.db import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Inside the User class
    log_entries = relationship("LogEntry", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    weekly_plans = relationship("WeeklyPlan", back_populates="user")
    # Add other fields as needed
