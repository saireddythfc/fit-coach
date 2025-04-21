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
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
async def chat_with_ai(
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
        .order_by(LogEntry.created_at.desc())
        .limit(5)
        .all()
    )

    # Construct context string
    context = f"Goal: {goal.description if goal else 'N/A'}\n"
    context += f"Weekly Plan Start: {plan.week_start if plan else 'N/A'}\n"
    context += "Recent Activities:\n"
    for log in logs:
        context += f"- Calories in:{log.calories_in} and Calories_out:{log.calories_out} at {log.created_at}\n"

    # Initialize AI Engine

    api_key = os.environ.get("FETCHAI_API_KEY")
    email_id = os.environ.get("FETCHAI_EMAIL")

    ai_engine = AiEngine(api_key)

    function_groups = await ai_engine.get_function_groups()
    functionGroupId = None

    for group in function_groups:
        if group.name == "Fetch Verified":
            functionGroupId = group.uuid
            break

    if functionGroupId is None:
        raise Exception('Could not find "Public" function group.')

    # Create session
    session = await ai_engine.create_session(function_group=functionGroupId)
    await session.start(objective=query.get("message"), context=context)

    # Retrieve response
    messages = await session.get_messages()
    if messages:
        return {"response": messages[-1].content}
    else:
        raise HTTPException(status_code=500, detail="No response from AI Engine")
