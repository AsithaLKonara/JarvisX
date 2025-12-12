"""
Chat API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.middleware.auth import get_current_user
from app.schemas.chat import (
    MessageCreate,
    MessageResponse,
    ConversationCreate,
    ConversationResponse,
    ChatResponse,
)
from app.services.chat_service import (
    process_chat_message,
    get_conversations,
    get_messages,
    delete_conversation,
    get_or_create_conversation,
)
import json

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/messages", response_model=ChatResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a chat message and get AI response"""
    user_message, assistant_message = await process_chat_message(
        db,
        current_user.id,
        message_data
    )
    
    # Get conversation
    conversation = get_or_create_conversation(
        db,
        current_user.id,
        assistant_message.conversation_id
    )
    
    return ChatResponse(
        message=MessageResponse(
            id=str(assistant_message.id),
            conversation_id=str(assistant_message.conversation_id),
            role=assistant_message.role,
            content=assistant_message.content,
            created_at=assistant_message.created_at,
        ),
        conversation=ConversationResponse(
            id=str(conversation.id),
            user_id=str(conversation.user_id),
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(conversation.messages),
        )
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    conversations = get_conversations(db, current_user.id, limit, offset)
    
    return [
        ConversationResponse(
            id=str(conv.id),
            user_id=str(conv.user_id),
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages),
        )
        for conv in conversations
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages from a conversation"""
    import uuid
    try:
        conv_id = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )
    
    messages = get_messages(db, conv_id, current_user.id, limit, offset)
    
    return [
        MessageResponse(
            id=str(msg.id),
            conversation_id=str(msg.conversation_id),
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    import uuid
    try:
        conv_id = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )
    
    success = delete_conversation(db, conv_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"message": "Conversation deleted successfully"}


@router.websocket("/ws/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract token and message
            token = message_data.get("token")
            content = message_data.get("content")
            
            if not token or not content:
                await websocket.send_json({
                    "error": "Missing token or content"
                })
                continue
            
            # Verify token and get user (simplified - in production, use proper auth)
            # For now, we'll process without full auth in WebSocket
            # In production, implement proper WebSocket authentication
            
            # Process message (simplified version)
            try:
                from core.unified_orchestrator import UnifiedOrchestrator
                orchestrator = UnifiedOrchestrator()
                result = orchestrator.process_text_command(content, enable_tts=False)
                response = result.get("response", "I couldn't process that.")
            except Exception as e:
                response = f"Error: {str(e)}"
            
            # Send response
            await websocket.send_json({
                "role": "assistant",
                "content": response,
                "timestamp": str(datetime.utcnow())
            })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "error": str(e)
        })

