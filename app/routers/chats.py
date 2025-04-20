import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from ai_engine_sdk import AiEngine
from app.db import get_db
from app.models.users import User
from app.models.goals import Goal
from app.models.weekly_plans import WeeklyPlan
from app.models.log_entries import LogEntry


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
def chat_with_ai(
    query: dict, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch user context
    goal = (
        db.query(Goal)
        .filter_by(user_id=user.id)
        .order_by(Goal.created_at.desc())
        .first()
    )
    plan = (
        db.query(WeeklyPlan)
        .filter_by(user_id=user.id)
        .order_by(WeeklyPlan.created_at.desc())
        .first()
    )
    logs = (
        db.query(LogEntry)
        .filter_by(user_id=user.id)
        .order_by(LogEntry.timestamp.desc())
        .limit(5)
        .all()
    )

    # Construct context string
    context = f"Goal: {goal.description if goal else 'N/A'}\n"
    context += f"Weekly Plan Start: {plan.week_start if plan else 'N/A'}\n"
    context += "Recent Activities:\n"
    for log in logs:
        context += f"- {log.action} at {log.timestamp}\n"

    # Initialize AI Engine
    api_key = os.getenv("FETCHAI_API_KEY")
    email = os.getenv("FETCHAI_EMAIL")
    function_group = os.getenv("FETCHAI_FUNCTION_GROUP")
    ai_engine = AiEngine(api_key)

    # Create session
    session = ai_engine.create_session(
        email=email, requested_model="talkative-01", function_group=function_group
    )
    session.start(objective=query.get("message"), context=context)

    # Retrieve response
    messages = session.get_messages()
    if messages:
        return {"response": messages[-1].content}
    else:
        raise HTTPException(status_code=500, detail="No response from AI Engine")
