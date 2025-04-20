# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from app.db import get_db
from app.models.users import User
from app.schemas.users import UserLogin, UserRead, UserCreate
from app.core.security import (
    verify_password,
    create_access_token,
    hash_password,
    JWTSettings,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@AuthJWT.load_config
def get_config():
    return JWTSettings()


@router.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user with the same username already exists
    db_user_username = db.query(User).filter(User.username == user.username).first()
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check if user with the same email already exists
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create a new user in the database
    db_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
async def login_user(
    user: UserLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = await create_access_token(
        subject=db_user.username, Authorize=Authorize
    )
    return {"access_token": access_token}
