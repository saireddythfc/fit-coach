# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator  # for type hinting

# 1. Database URL (adjust user/password/host/dbname as needed)
DATABASE_URL = "postgresql://user:password@localhost/fitcoach"

# 1. Create the declarative base
Base = (
    declarative_base()
)  # constructs a base class for ORM models :contentReference[oaicite:0]{index=0}


# 2. Create SQLAlchemy engine & session factory
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# 3. Define get_db dependency
def get_db() -> Generator:
    """
    FastAPI dependency that yields a DB session,
    then closes it when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
