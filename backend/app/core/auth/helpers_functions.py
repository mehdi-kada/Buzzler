from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException, status, Response
from passlib.context import CryptContext
from jose import JWTError, jwt

from email.message import EmailMessage
import aiosmtplib
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def hash_token(token: str) -> str:
    return pwd_context.hash(token)


def verify_hash_token(token: str, hashed_token: str) -> bool:
    return pwd_context.verify(token, hashed_token)


def _timestamp_from_delta(delta: timedelta) -> int:
    """Return a unix timestamp (int) for now + delta."""
    expire = datetime.utcnow() + delta
    return int(expire.timestamp())


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token.

    The `exp` claim is set as an integer unix timestamp to avoid
    JSON serialization issues and to satisfy JWT expectations.
    """
    to_encode = data.copy()
    exp_ts = _timestamp_from_delta(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": exp_ts, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    The `exp` claim is an integer unix timestamp.
    """
    to_encode = data.copy()
    exp_ts = _timestamp_from_delta(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": exp_ts, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_verification_token(email: str) -> str:
    """
    Generate an account verification JWT with integer `exp` claim.
    """
    data: Dict[str, Any] = {"sub": email, "type": "verification"}
    exp_ts = _timestamp_from_delta(timedelta(hours=24))
    data.update({"exp": exp_ts})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _normalize_samesite(value: Optional[str]) -> Optional[str]:
    """
    Normalize a configured samesite value into the accepted literal strings
    used by Starlette/FastAPI: 'lax', 'strict', 'none'. Return None if
    the provided value is not valid.
    """
    if not value:
        return None
    v = value.strip().lower()
    if v in ("lax", "strict", "none"):
        return v
    return None


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """
    Set the refresh token as an HttpOnly cookie.

    The samesite value is normalized to one of 'lax', 'strict', 'none' or
    left as None to let the framework default.
    """
    samesite_val = _normalize_samesite(getattr(settings, "COOKIE_SAMESITE", None))
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=getattr(settings, "SECURE_COOKIES", False),  # should be True in production
        samesite=samesite_val,
        domain=getattr(settings, "COOKIE_DOMAIN", None),
        max_age=int(getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7) * 24 * 60 * 60),
    )


def clear_refresh_cookie(response: Response) -> None:
    """
    Clear the refresh token cookie by expiring it.
    """
    samesite_val = _normalize_samesite(getattr(settings, "COOKIE_SAMESITE", None))
    response.set_cookie(
        key="refresh_token",
        value="",
        expires=0,
        httponly=True,
        secure=getattr(settings, "SECURE_COOKIES", False),
        samesite=samesite_val,
        domain=getattr(settings, "COOKIE_DOMAIN", None),
    )


async def send_verification_email(email: str, token: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "Verify Your Buzzler Account"
    verification_url = f"{settings.BACKEND_URL}/auth/verify-account?token={token}"

    plain_text_content = f"Please verify your email by clicking this link: {verification_url}"
    message.set_content(plain_text_content)

    html_content = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Thank you for registering with Buzzler. Please verify your email by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Your Account</a></p>
            <p>If you cannot click the link, please copy and paste this URL into your browser:</p>
            <p>{verification_url}</p>
            <p>Thanks,<br>The Buzzler Team</p>
        </body>
    </html>
    """
    message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        use_tls=False,
    )


async def send_password_verification_email(email: str, token: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "Reset your Buzzler account password"
    verification_url = f"{settings.BACKEND_URL}/auth/password-reset?token={token}"

    plain_text_content = f"You can reset your password by clicking on this link: {verification_url}"
    message.set_content(plain_text_content)

    html_content = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>You requested a password reset for your Buzzler account. Please click the link below to proceed:</p>
            <p><a href="{verification_url}">Reset Your Password</a></p>
            <p>If you cannot click the link, please copy and paste this URL into your browser:</p>
            <p>{verification_url}</p>
            <p>If you did not request this, please ignore this email.</p>
            <p>Thanks,<br>The Buzzler Team</p>
        </body>
    </html>
    """
    message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        use_tls=False,
    )


async def issue_tokens_and_set_cookie(user: Any, response: Response, db: Any) -> str:
    """
    Create access and refresh tokens, store a hashed refresh token on the user,
    commit the change, and set the refresh token cookie.
    """
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    # store hashed refresh token on the user model (ORM-managed attribute)
    setattr(user, "refresh_token", hash_token(refresh_token))
    await db.commit()

    set_refresh_token_cookie(response, refresh_token)

    return access_token
