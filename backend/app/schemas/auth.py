"""
Authentication schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None


class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class OAuthLogin(BaseModel):
    """OAuth login schema"""
    provider: str  # google, apple, facebook
    token: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    
    class Config:
        from_attributes = True

