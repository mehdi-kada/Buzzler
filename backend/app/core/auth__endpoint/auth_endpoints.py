# Depenedcry to get user (verify them )
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.auth import verify_token


router = APIRouter(prefix="/auth", tags=["auth"])
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = verify_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect token type"
        )
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid Token"
        )
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Inactive user"
        )
    return user 