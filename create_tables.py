from app.db import engine, Base
from app.models import User, LogEntry, Goal, WeeklyPlan

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Tables created.")
