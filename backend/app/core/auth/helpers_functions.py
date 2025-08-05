from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException, status, Response
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import Settings
from email.message import EmailMessage
import aiosmtplib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str)-> bool:
    return pwd_context.verify(password, hashed_password)

def hash_token(token: str) -> str:
    return pwd_context.hash(token)

def verify_hash_token(token: str, hashed_token: str)-> bool:
    return pwd_context.verify(token, hashed_token)

def create_access_token(data:dict) ->str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire, "type":"access"})
    return jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)

def create_refresh_token(data:dict) -> str : 
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=Settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type":"refresh"})
    return jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOken",
            headers={"WWW-Authenticate": "Bearer"},
        )

# this a token for email verification
def generate_verification_token() -> str:
    return str(uuid.uuid4())

def set_refresh_token_cookie(response: Response, refresh_token:str) :
    response.set_cookie(
        key= "refresh_token",
        value=refresh_token,
        httponly=True,
        secure=Settings.SECURE_COOKIES,  # set to true in production
        samesite=Settings.COOKIE_SAMESITE,
        domain=Settings.COOKIE_DOMAIN,
        max_age=Settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

def clear_refresh_cookie(response: Response):
    response.set_cookie(
        key="refresh_token",
        value="",
        expires=0,
        httponly=True,
        secure=Settings.SECURE_COOKIES,
        samesite=Settings.COOKIE_SAMESITE,
        domain=Settings.COOKIE_DOMAIN
    )


async def send_verification_email(email:str, token:str):
    message = EmailMessage()
    message["From"] = Settings.SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "Verify Your Buzzler Account"
    verification_url = f"http://localhost:3000/auth//verify-account?token={token}"
    message.set_content(f"Please verify your email by clicking this link : {verification_url}")

    await aiosmtplib.send(
        message,
        hostname=Settings.SMTP_HOST,
        port=Settings.SMTP_PORT,
        username=Settings.SMTP_USERNAME,
        password=Settings.SMTP_PASSWORD,
        use_tls=True,
    )

async def send_password_verification_email(email:str, token:str):
    message = EmailMessage()
    message["From"] = Settings.SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "Reset your Buzzler account password"
    verification_url = f"http://localhost:3000/auth/password-reset?token={token}"
    message.set_content(f"You can reset your password by clicking on this link: {verification_url}")

    await aiosmtplib.send(
        message,
        hostname=Settings.SMTP_HOST,
        port=Settings.SMTP_PORT,
        username=Settings.SMTP_USERNAME,
        password=Settings.SMTP_PASSWORD,
        use_tls=True,
    )

async def issue_tokens_and_set_cookie(user, response: Response, db) -> str:
    """Creates tokens, stores the refresh token hash, and sets the cookie."""
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    user.refresh_token = hash_token(refresh_token)
    await db.commit()
    
    set_refresh_token_cookie(response, refresh_token)
    
    return access_token
