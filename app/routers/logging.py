# app/routers/logging.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db  # ← now valid
from app.models.models import LogEntry  # your ORM model

router = APIRouter()


@router.post("/log-entry")
def create_log_entry(
    calories_in: int,
    calories_out: int,
    db: Session = Depends(get_db),  # injects a working DB session
):
    entry = LogEntry(calories_in=calories_in, calories_out=calories_out)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
