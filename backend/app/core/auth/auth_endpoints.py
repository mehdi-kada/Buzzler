from datetime import datetime, timedelta
import logging
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode

from jose import jwt, JWTError

from app.db.database import get_db
from app.models.user import AuthProviders, User
from app.core.auth.helpers_functions import (
    clear_refresh_cookie,
    create_access_token,
    create_refresh_token,
    generate_verification_token,
    hash_password,
    hash_token,
    issue_tokens_and_set_cookie,
    send_password_verification_email,
    send_verification_email,
    set_refresh_token_cookie,
    verify_hash_token,
    verify_password,
    verify_token,
)
from app.schemas.schema_user import EmailSchema, PasswordReset, TokenResponse, UserBase, UserResponse
from app.config import settings as Settings
from app.core.auth.providers import get_provider
from app.core.security.csrf import csrf_protection

logger = logging.getLogger(__name__)

router = APIRouter()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Dependency to retrieve and validate the current user from an access token.
    """
    payload = verify_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token type")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not getattr(user, "is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive user")

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserBase, response: Response, db: AsyncSession = Depends(get_db)):
    """Register a new user and send a verification email."""
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    hashed_password = hash_password(user_data.password)
    verification_token = generate_verification_token(user_data.email)

    new_user = User(
        email=user_data.email,
        password_hashed=hashed_password,
        first_name=user_data.first_name,
        auth_provider=AuthProviders.EMAIL,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # send the verification email (fire-and-forget)
    await send_verification_email(new_user.email, verification_token)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(response: Response, user_form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Log a user in, issue tokens and set refresh token cookie.
    """
    result = await db.execute(select(User).where(User.email == user_form.username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Work with local typed copies of possibly-ORM-mapped datetime attributes
    account_lockout_expiry = cast(Optional[datetime], getattr(user, "account_lockout_expiry", None))
    if account_lockout_expiry:
        if account_lockout_expiry > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked until {account_lockout_expiry}",
            )
        # reset lockout fields via setattr to avoid static type issues with ORM descriptors
        setattr(user, "failed_login_attempts", 0)
        setattr(user, "account_lockout_expiry", None)

    hashed_pw = getattr(user, "password_hashed", None)
    # narrow the optional before calling verify_password to satisfy typing
    if not hashed_pw or not verify_password(user_form.password, cast(str, hashed_pw)):
        # increment failed attempts
        failed_attempts = cast(int, getattr(user, "failed_login_attempts", 0)) + 1
        setattr(user, "failed_login_attempts", failed_attempts)

        if failed_attempts >= 5:
            lock_until = datetime.utcnow() + timedelta(hours=1)
            setattr(user, "account_lockout_expiry", lock_until)
            await db.commit()
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account locked")

        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not getattr(user, "is_verified", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not verified")

    # reset the failed attempts and update last login timestamp
    setattr(user, "failed_login_attempts", 0)
    setattr(user, "last_login_at", datetime.utcnow())
    setattr(user, "account_lockout_expiry", None)

    # Issue tokens and set refresh cookie (helper may be async)
    access_token = await issue_tokens_and_set_cookie(user, response, db)

    # Also generate a CSRF token and set cookie (double-submit)
    csrf_token = csrf_protection.generate_csrf_token()
    csrf_protection.set_csrf_cookie(response, csrf_token)

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Refresh the access token using the refresh token from an HttpOnly cookie.
    """
    # enforce CSRF for cookie auth action
    if not csrf_protection.verify_csrf_protection(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided. Please log in again.")

    try:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        stored_refresh_hash = getattr(user, "refresh_token", None)
        # ensure the stored hash is a str before passing to verify_hash_token
        if not user or not stored_refresh_hash or not verify_hash_token(refresh_token, cast(str, stored_refresh_hash)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # generate a new access token and refresh token
        access_token = create_access_token(data={"sub": user.email})
        new_refresh_token = create_refresh_token(data={"sub": user.email})
        setattr(user, "refresh_token", hash_token(new_refresh_token))
        await db.commit()

        set_refresh_token_cookie(response, new_refresh_token)

        return TokenResponse(access_token=access_token, token_type="bearer")
    except Exception:
        # Clear invalid refresh token cookie to force re-login
        clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token. Please log in again.")


@router.post("/logout")
async def log_out(request: Request, response: Response, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # CSRF verify for state-changing action
    if not csrf_protection.verify_csrf_protection(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")

    setattr(user, "refresh_token", None)
    await db.commit()
    clear_refresh_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/verify-account")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        if payload.get("type") != "verification":
            raise ValueError("Invalid token type")

        email = payload.get("sub")
        if not email:
            raise ValueError("Invalid token")
    except (JWTError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token") from e

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    setattr(user, "is_verified", True)
    await db.commit()
    return RedirectResponse("http://localhost:3000/auth/verify-account?status=success")


@router.post("/password-reset-request")
async def password_reset_request(data: EmailSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()
    if user:
        # Create a password reset token (JWT) that includes email and type
        reset_claims = {
            "sub": user.email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        raw_token = jwt.encode(reset_claims, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
        setattr(user, "password_reset_token", hash_token(raw_token))
        setattr(user, "password_reset_expires_at", datetime.utcnow() + timedelta(hours=1))
        await db.commit()

        await send_password_verification_email(user.email, raw_token)

    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/password-reset")
async def password_reset(data: PasswordReset, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(data.token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    password_reset_expires_at = cast(Optional[datetime], getattr(user, "password_reset_expires_at", None))
    if not user or not getattr(user, "password_reset_token", None) or not password_reset_expires_at or password_reset_expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    stored_prt = getattr(user, "password_reset_token", None)
    # we've already checked presence earlier, but narrow type for the verifier
    if not verify_hash_token(data.token, cast(str, stored_prt)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    setattr(user, "password_hashed", hash_password(data.password))
    setattr(user, "password_reset_token", None)
    setattr(user, "password_reset_expires_at", None)
    await db.commit()
    return {"message": "Password reset successfully"}


@router.get("/google/login")
async def google_login():
    params = {
        "client_id": Settings.GOOGLE_CLIENT_ID,
        "redirect_uri": Settings.REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"redirect_url": google_auth_url}


@router.get("/oauth/callback")
async def oauth_callback(code: str, provider: str, response: Response, db: AsyncSession = Depends(get_db)):
    """Handle OAuth callback and redirect user to the frontend."""
    try:
        oauth_provider = get_provider(provider)
        # exchange the code for an access token and user info
        user_data = await oauth_provider.get_user_info(code)

        email = user_data["email"]
        oauth_id = user_data["oauth_id"]
        first_name = user_data.get("first_name", "User")

        if provider == "google":
            auth_provider = AuthProviders.GOOGLE
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")

        result = await db.execute(select(User).where(User.oauth_id == oauth_id))
        user = result.scalars().first()

        if not user:
            # check if the email exists with any provider, if it does link it to user account
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalars().first()

            if existing_user:
                setattr(existing_user, "oauth_id", oauth_id)
                setattr(existing_user, "auth_provider", auth_provider)
                setattr(existing_user, "is_verified", True)
                user = existing_user
                await db.commit()
            else:
                user = User(
                    email=email,
                    oauth_id=oauth_id,
                    auth_provider=auth_provider,
                    first_name=first_name,
                    is_verified=True,
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

        access_token = create_access_token(data={"sub": user.email})

        frontend_url = "http://localhost:3000/auth/oauth/success"
        # put user details as query params (flattened)
        user_params = urlencode({"email": user.email, "first_name": user.first_name})
        redirect_url = f"{frontend_url}?token={access_token}&{user_params}"

        return RedirectResponse(url=redirect_url, status_code=302)

    except Exception as e:
        logger.exception("OAuth callback error")
        error_query = urlencode({"message": str(e)})
        error_url = f"http://localhost:3000/auth/login?error={error_query}"
        return RedirectResponse(url=error_url, status_code=302)


@router.post("/setup-session")
async def setup_session(response: Response, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Setup session with refresh token cookie after OAuth login.
    """
    refresh_token = create_refresh_token(data={"sub": user.email})

    setattr(user, "refresh_token", hash_token(refresh_token))
    await db.commit()

    set_refresh_token_cookie(response, refresh_token)

    csrf_token = csrf_protection.generate_csrf_token()
    csrf_protection.set_csrf_cookie(response, csrf_token)

    return {"message": "Session setup successful", "csrf_token": csrf_token}


@router.get("/csrf-token")
async def generate_csrf_token(request: Request, response: Response):
    csrf_token = csrf_protection.generate_csrf_token()
    csrf_protection.set_csrf_cookie(response, csrf_token)

    return {"csrf_token": csrf_token, "header_name": Settings.CSRF_HEADER_NAME}
