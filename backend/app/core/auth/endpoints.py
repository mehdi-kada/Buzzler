# Depenedcry to get user (verify them )
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import AuthProviders, User
from app.core.auth.helpers_functions import create_access_token, create_refresh_token, generate_refresh_token, hash_password, hash_token, set_refresh_token_cookie, verify_password, verify_token
from app.schemas.user import TokenResponse, UserBase, UserResponse


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

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED )
async def register(user_data: UserBase , db: AsyncSession= Depends(get_db), response: Response = None ):
    """ register user and send verification email """
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
        auth_provider= AuthProviders.EMAIL,
        email_verification_token= verification_token,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # send the verification email 
    #await send_verification_email(new_user.email, verification_token)

    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(response: Response ,user_form: OAuth2PasswordRequestForm = Depends() ,  db: AsyncSession= Depends(get_db)):
    """
    Logs user in, returns access token and sets refresh token in cookie.
    """
    result = await db.execute(select(User).where(User.email == user_form.email))
    user = result.scalars().first()
    if not user or not verify_password(user_form.password, user.password_hashed) : 
        if user:
            user.failed_login_attempts += 1
            await db.commit()
            if user.failed_login_attempts >= 5:
                raise HTTPException(
                    status_code= status.HTTP_403_FORBIDDEN,
                    detail= "account locked"
                )
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid Credentials"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "email not verified"
        )
    
    user.failed_login_attempts= 0
    user.last_login_at= datetime.utcnow()

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    user.refresh_token = hash_token(refresh_token)
    await db.commit()

    set_refresh_token_cookie(response, refresh_token)

    return TokenResponse(access_token=access_token, token_type="bearer")
