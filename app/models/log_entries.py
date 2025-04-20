from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
from users import User
import datetime


class LogEntry(Base):
    __tablename__ = "log_entries"  # table name in the database

    # 2. Primary key column
    id = Column(
        Integer, primary_key=True, index=True
    )  # unique identifier :contentReference[oaicite:1]{index=1}

    # 3. Foreign key to a User table (assumes you have a 'users' table with 'id')
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 4. The date for this log (defaults to today)
    date = Column(Date, default=datetime.date.today, nullable=False)

    # 5. Calories consumed and burned
    calories_in = Column(Integer, nullable=False)
    calories_out = Column(Integer, nullable=False)

    # 6. Timestamp when this record was created
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="log_entries")
