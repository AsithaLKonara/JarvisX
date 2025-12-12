"""
User schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: EmailStr
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    created_at: str
    
    class Config:
        from_attributes = True

