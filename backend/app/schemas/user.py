from pydantic import BaseModel, EmailStr


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

class EmailSchema(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

