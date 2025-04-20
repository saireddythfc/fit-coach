# app/routers/goal.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from app.db import get_db
from app.models.users import User
from app.models.goals import Goal
from app.schemas.goals import GoalCreate, GoalRead

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.get("/test")
async def test_goals_route():
    return {"message": "Goals router is working!"}


@router.post("/", response_model=GoalRead)
async def set_goal(
    goal: GoalCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    current_user_username = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user_username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_goal = Goal(user_id=db_user.id, **goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/me", response_model=GoalRead)
async def get_user_goal(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user_username = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user_username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    goal = db.query(Goal).filter(Goal.user_id == db_user.id).first()
    return goal
