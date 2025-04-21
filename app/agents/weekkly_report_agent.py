from fetchai.agents.api import AgentAPI, OEEService
from fetchai.connections import StubConnection  # Or a proper connection
from fetchai.crypto.entity import Entity
import asyncio
import json
import os  # For environment variables within the agent

# Import your database models and potentially database session factory here
from app.models import User, LogEntry, Goal, WeeklyPlan
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

SERVICE_ID = "generate_weekly_report"
PROTOCOL_ID = "fitness_reporting"
DATABASE_URL = "postgresql://user:password@localhost/fitcoach"


class WeeklyReportAgent:
    def __init__(self, agent_api: AgentAPI):
        self.api = agent_api
        self.oee_service = OEEService(self.api.oee)
        # Initialize database engine and session factory within the agent
        self.engine = create_engine(DATABASE_URL)  # Configure your DB URL
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.ai_engine = None  # Initialize in run method

    def get_db(self):
        db = self.SessionLocal()
        try:
            return db
        finally:
            db.close()

    async def generate_report_handler(self, query, sender):
        print(
            f"WeeklyReportAgent received report request for user: {query.get('user_id')}"
        )
        user_id = query.get("user_id")
        if not user_id:
            return {"error": "Missing user_id in the report request."}

        db = self.get_db()
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {"error": f"User with id {user_id} not found."}

        # 1. Gather context
        logs = (
            db.query(LogEntry)
            .filter_by(user_id=user.id)
            .order_by(LogEntry.date.desc())
            .limit(7)
            .all()
        )
        goal = db.query(Goal).filter_by(user_id=user.id).first()
        plan = db.query(WeeklyPlan).filter_by(user_id=user.id).first()
        context = {
            "logs": [l._asdict() for l in logs],
            "goal": goal.description if goal else None,
            "plan_start": plan.week_start.isoformat() if plan else None,
        }

        # 2. Start AI Engine session
        if not self.ai_engine:
            api_key = os.getenv("FETCHAI_API_KEY")
            self.ai_engine = AiEngine(api_key)

        session = await self.ai_engine.create_session(
            function_group=os.getenv("FUNCTION_GROUP_ID")
        )
        await session.start(
            objective="Generate weekly fitness report", context=json.dumps(context)
        )

        # 3. Message loop to get report
        report = None
        from ai_engine_sdk import (
            is_task_selection_message,
            is_confirmation_message,
            is_agent_message,
        )

        while True:
            msgs = await session.get_messages()
            for m in msgs:
                if is_task_selection_message(m):
                    await session.submit_task_selection(m, [m.options["0"]])
                elif is_confirmation_message(m):
                    await session.submit_confirmation(m)
                elif is_agent_message(m):
                    report = json.loads(m.content)
                    break
            if report:
                break
            await asyncio.sleep(1)
        return {"report": report}

    async def run(self):
        await self.oee_service.register_service(
            SERVICE_ID,
            PROTOCOL_ID,
            {"description": "Generates personalized weekly fitness reports"},
        )
        await self.oee_service.bind_service(
            SERVICE_ID, PROTOCOL_ID, self.generate_report_handler
        )
        print(f"WeeklyReportAgent service '{SERVICE_ID}' registered.")

        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.api.stop()


async def main():
    private_key = Entity()
    agent_api = AgentAPI(
        private_key.public_key(), StubConnection()
    )  # Replace with proper connection
    report_agent = WeeklyReportAgent(agent_api)
    await report_agent.run()


if __name__ == "__main__":
    asyncio.run(main())
