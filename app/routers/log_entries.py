from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from datetime import date
from app.db import get_db
from app.models.log_entries import LogEntry
from app.schemas.log_entries import LogEntryCreate, LogEntryRead
from app.models.users import User

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/", response_model=LogEntryRead)
def create_log(
    payload: LogEntryCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(404, "User not found")
    entry = LogEntry(user_id=user.id, **payload.dict())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/me", response_model=list[LogEntryRead])
def read_my_logs(
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(404, "User not found")
    q = db.query(LogEntry).filter_by(user_id=user.id)
    if start:
        q = q.filter(LogEntry.date >= start)
    if end:
        q = q.filter(LogEntry.date <= end)
    return q.order_by(LogEntry.date.desc()).all()
