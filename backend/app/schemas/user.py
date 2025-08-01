from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    password : str
    first_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class PasswordReset(BaseModel):
    token: str
    new_password: str

