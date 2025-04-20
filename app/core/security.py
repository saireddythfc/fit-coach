# core/security.py
from datetime import timedelta
from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from pydantic_settings import BaseSettings

ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTSettings(BaseSettings):
    authjwt_secret_key: str = "YOUR_SECRET_KEY"  # Replace with a strong, secret key
    authjwt_access_token_expires: timedelta = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Add other settings as needed (e.g., cookie settings)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(subject: str, Authorize: AuthJWT = Depends()):
    """Generates a new access token."""
    return Authorize.create_access_token(subject=subject)
