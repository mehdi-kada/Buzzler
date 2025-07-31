from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class AuthProviders(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    X = "twitter"

class UserCreate(BaseModel):
    email: EmailStr
    password_hashed: Optional[str] = None
    auth_provider: AuthProviders = AuthProviders.EMAIL
    oauth_id: Optional[str] = None
    first_name: str
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    email_verification_token: str
    password_reset_token: Optional[str] = None
