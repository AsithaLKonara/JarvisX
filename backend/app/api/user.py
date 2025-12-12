"""
User API endpoints
"""
from fastapi import APIRouter, Depends
from app.models.user import User
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified == "true",
        created_at=current_user.created_at.isoformat(),
    )

