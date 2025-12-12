"""
Billing API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])


class SubscriptionResponse(BaseModel):
    """Subscription response schema"""
    plan: str
    status: str  # 'active', 'canceled', 'past_due'
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool


class UsageResponse(BaseModel):
    """Usage response schema"""
    messages_used: int
    messages_limit: int
    conversations_count: int


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription"""
    # TODO: Implement billing/subscription logic
    return SubscriptionResponse(
        plan="pro",
        status="active",
        current_period_start=datetime.utcnow().isoformat(),
        current_period_end=(datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=1).isoformat(),
        cancel_at_period_end=False
    )


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics"""
    from sqlalchemy import func
    from app.models.chat import Message, Conversation
    
    # Get message count for current period
    messages_used = db.query(func.count(Message.id)).join(Conversation).filter(
        Conversation.user_id == current_user.id
    ).scalar() or 0
    
    conversations_count = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id
    ).scalar() or 0
    
    # TODO: Get actual limits from subscription
    messages_limit = 10000
    
    return UsageResponse(
        messages_used=messages_used,
        messages_limit=messages_limit,
        conversations_count=conversations_count
    )


@router.post("/upgrade")
async def upgrade_subscription(
    plan: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade subscription plan"""
    # TODO: Implement subscription upgrade
    return {
        "message": f"Subscription upgraded to {plan}",
        "plan": plan
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    # TODO: Implement subscription cancellation
    return {
        "message": "Subscription will be canceled at the end of current period"
    }

