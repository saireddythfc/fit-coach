from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fetchai.agents.api import AgentAPI, OEEService
from fetchai.connections import StubConnection  # Or your configured connection
from fetchai.crypto.entity import Entity
from app.db import get_db
from app.models import User
import asyncio, os

router = APIRouter(prefix="/report", tags=["Reports"])

# Initialize Fetch.ai agent for your backend (can be a long-running process)
backend_private_key = Entity()
backend_agent = AgentAPI(backend_private_key.public_key(), StubConnection())
backend_oee_service = OEEService(backend_agent.oee)


async def get_weekly_report_from_agent(user_id: int):
    # 1. Discover the WeeklyReportAgent service
    search_result = await backend_oee_service.search_services(
        "generate_weekly_report", "fitness_reporting", {}
    )

    if search_result:
        report_agent_address = search_result[0]["address"]
        print(f"Found WeeklyReportAgent at: {report_agent_address}")

        # 2. Send a query to the WeeklyReportAgent with the user_id
        query = {"user_id": user_id}
        response = await backend_agent.send_message(
            {
                "protocol": "fitness_reporting",
                "service": "generate_weekly_report",
                "action": "query",
                "content": query,
            },
            report_agent_address,
            timeout=10,  # Adjust timeout as needed
        )

        if response and "content" in response and "report" in response["content"]:
            return response["content"]["report"]
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get weekly report from agent: {response}",
            )
    else:
        raise HTTPException(
            status_code=503, detail="WeeklyReportAgent service not found."
        )


@router.post("/")
async def generate_weekly_report(
    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    report = await get_weekly_report_from_agent(user.id)
    return report


# Ensure your backend agent is started (you might need a background task in main.py)
async def startup_event():
    await backend_agent.start()


async def shutdown_event():
    await backend_agent.stop()


# You'll need to add these to your FastAPI app instance in main.py
# app.add_event_handler("startup", startup_event)
# app.add_event_handler("shutdown", shutdown_event)
