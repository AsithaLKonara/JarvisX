"""
Analytics API endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.chat import Message, Conversation
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/usage")
async def get_usage_stats(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics for the user"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Message count by date
    messages_by_date = db.query(
        func.date(Message.created_at).label('date'),
        func.count(Message.id).label('count')
    ).join(Conversation).filter(
        and_(
            Conversation.user_id == current_user.id,
            Message.created_at >= start_date
        )
    ).group_by(
        func.date(Message.created_at)
    ).all()
    
    # Total stats
    total_messages = db.query(func.count(Message.id)).join(Conversation).filter(
        and_(
            Conversation.user_id == current_user.id,
            Message.created_at >= start_date
        )
    ).scalar() or 0
    
    total_conversations = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.user_id == current_user.id,
            Conversation.created_at >= start_date
        )
    ).scalar() or 0
    
    return {
        "period_days": days,
        "total_messages": total_messages,
        "total_conversations": total_conversations,
        "messages_by_date": [
            {"date": str(date), "count": count}
            for date, count in messages_by_date
        ]
    }


@router.get("/mode-usage")
async def get_mode_usage(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics by mode"""
    # For now, return mock data since mode isn't stored in messages
    # TODO: Add mode field to messages/conversations
    return {
        "period_days": days,
        "modes": [
            {"name": "Engineer", "usage": 35, "percentage": 35},
            {"name": "Business", "usage": 25, "percentage": 25},
            {"name": "Designer", "usage": 15, "percentage": 15},
            {"name": "System Monitor", "usage": 12, "percentage": 12},
            {"name": "Editor", "usage": 8, "percentage": 8},
            {"name": "Career", "usage": 5, "percentage": 5},
        ]
    }


@router.get("/response-time")
async def get_response_time_stats(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get average response time statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Calculate average response time per day
    # This is simplified - in production, you'd track actual response times
    messages_by_date = db.query(
        func.date(Message.created_at).label('date'),
        func.count(Message.id).label('count')
    ).join(Conversation).filter(
        and_(
            Conversation.user_id == current_user.id,
            Message.created_at >= start_date,
            Message.role == 'assistant'
        )
    ).group_by(
        func.date(Message.created_at)
    ).all()
    
    # Mock average response time (1.0-1.3 seconds)
    import random
    response_times = [
        {"date": str(date), "avg": round(random.uniform(1.0, 1.3), 2)}
        for date, count in messages_by_date
    ]
    
    return {
        "period_days": days,
        "response_times": response_times,
        "average": round(sum(r["avg"] for r in response_times) / len(response_times) if response_times else 1.2, 2)
    }

