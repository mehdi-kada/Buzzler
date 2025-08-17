from fastapi import APIRouter, Depends

from app.models.user import User
from app.core.auth.auth_endpoints import get_current_user
from app.schemas.schema_user import UserResponse

router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user
