"""
Chat schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    """Create message schema"""
    conversation_id: Optional[str] = None
    content: str


class MessageResponse(BaseModel):
    """Message response schema"""
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Create conversation schema"""
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Chat response with message"""
    message: MessageResponse
    conversation: ConversationResponse

