# Depenedcry to get user (verify them )
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.auth import generate_refresh_token, hash_password, verify_token
from backend.app.schemas.user import UserBase, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
        Dependency to get get the user 
    """
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

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserBase , db: AsyncSession= Depends(get_db), response: Response = None ):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Email already exists"
        )
    
    hashed_password = hash_password(user_data.password)
    verification_token = generate_refresh_token()
    new_user= User(
        email= user_data.email,
        password_hashed= hashed_password,
        first_name= user_data.first_name,
        auth_provider= "email",
        email_verification_token= verification_token,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh()

    # send the verification email 
    await send_verification_email(new_user.email, verification_token)

    return new_user