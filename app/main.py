from fastapi import FastAPI
from app.routers.logging import router as log_router

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(log_router, prefix="/api")
