"""
Settings API endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    """Settings update schema"""
    default_mode: str = None
    theme: str = None
    language: str = None
    notifications_enabled: bool = None
    voice_enabled: bool = None
    api_key: str = None


@router.get("")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    # For now, return default settings
    # TODO: Add settings table/model
    return {
        "default_mode": "engineer",
        "theme": "light",
        "language": "en",
        "notifications_enabled": True,
        "voice_enabled": True,
        "api_key": None,
    }


@router.patch("")
async def update_settings(
    settings: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    # TODO: Implement settings storage
    return {
        "message": "Settings updated successfully",
        **settings.dict(exclude_unset=True)
    }

