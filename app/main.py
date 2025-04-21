from fastapi import FastAPI
from app.routers.logging import router as log_router
from app.routers import auth, goal, log_entries, profile, weekly_plans, chats

app = FastAPI()


app.include_router(log_router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(goal.router, prefix="/api")
app.include_router(log_entries.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(weekly_plans.router, prefix="/api")
app.include_router(chats.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
