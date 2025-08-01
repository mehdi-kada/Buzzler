from datetime import datetime
import uuid
from fastapi import HTTPException, status, Response
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import Settings


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
    expire = datetime.utcnow() + datetime.timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire, "type":"access"})
    return jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)

def create_refresh_token(data:dict) -> str : 
    to_encode = data.copy()
    expire = datetime.utcnow() + datetime.timedelta(days=Settings.REFRESH_TOKEN_EXPIRE_DAYS)
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
    
def generate_refresh_token() -> str:
    return str(uuid.uuid4())

def set_refresh_token_cookie(response: Response, refresh_token:str) :
    response.set_cookie(
        key= "refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # set to true in production
        samesite="lax",
        domain=Settings.COOKIE_DOMAIN,
        max_age=Settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    )

def clear_refresh_cookie(response: Response):
    response.set_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,  # match from above
        samesite="lax",
        domain=Settings.COOKIE_DOMAIN
    )