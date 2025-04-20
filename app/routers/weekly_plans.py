from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from app.db import get_db
from app.models.weekly_plans import WeeklyPlan
from app.schemas.weekly_plans import WeeklyPlanCreate, WeeklyPlanRead
from app.models.users import User
from app.utils.calendar_quickstart import get_calendar_service

router = APIRouter(prefix="/plans", tags=["WeeklyPlans"])


@router.post("/", response_model=WeeklyPlanRead)
def create_plan(
    payload: WeeklyPlanCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(404, "User not found")

    plan = WeeklyPlan(user_id=user.id, week_start=payload.week_start)
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # (Optional) Push to Google Calendar
    service = get_calendar_service()
    # e.g., create a placeholder event
    body = {
        "summary": "Start of fitness week",
        "start": {"date": str(plan.week_start)},
        "end": {"date": str(plan.week_start)},
    }
    service.events().insert(calendarId="primary", body=body).execute()
    plan.events_synced = True
    db.commit()
    db.refresh(plan)

    return plan


@router.get("/me", response_model=list[WeeklyPlanRead])
def read_my_plans(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(404, "User not found")
    return db.query(WeeklyPlan).filter_by(user_id=user.id).all()
