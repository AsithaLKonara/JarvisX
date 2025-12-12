"""
Chat service - handles chat operations and AI integration
"""
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.chat import Conversation, Message
from app.models.user import User
from app.schemas.chat import MessageCreate, ConversationCreate
import sys
from pathlib import Path

# Add parent directory to path for JarvisX imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def get_or_create_conversation(
    db: Session,
    user_id: uuid.UUID,
    conversation_id: Optional[uuid.UUID] = None
) -> Conversation:
    """Get existing conversation or create new one"""
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        if conversation:
            return conversation
    
    # Create new conversation
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=user_id,
        title=None,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def create_message(
    db: Session,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    model_used: Optional[str] = None,
    tokens_used: Optional[int] = None
) -> Message:
    """Create a new message"""
    message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        role=role,
        content=content,
        model_used=model_used,
        tokens_used=tokens_used,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def create_conversation(
    db: Session,
    user_id: uuid.UUID,
    title: Optional[str] = None
) -> Conversation:
    """Create a new conversation"""
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=user_id,
        title=title,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(
    db: Session,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID
) -> Optional[Conversation]:
    """Get a single conversation"""
    return db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()


def get_conversations(
    db: Session,
    user_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None
) -> List[Conversation]:
    """Get user's conversations with optional search"""
    query = db.query(Conversation).filter(
        Conversation.user_id == user_id
    )
    
    if search:
        query = query.filter(
            Conversation.title.ilike(f"%{search}%")
        )
    
    return query.order_by(
        Conversation.updated_at.desc()
    ).offset(offset).limit(limit).all()


def update_conversation(
    db: Session,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    title: Optional[str] = None
) -> Optional[Conversation]:
    """Update a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()
    
    if not conversation:
        return None
    
    if title is not None:
        conversation.title = title
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    return conversation


def get_messages(
    db: Session,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0
) -> List[Message]:
    """Get messages from a conversation"""
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()
    
    if not conversation:
        return []
    
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.asc()
    ).offset(offset).limit(limit).all()


async def process_chat_message(
    db: Session,
    user_id: uuid.UUID,
    message_data: MessageCreate
) -> tuple[Message, Message]:
    """Process chat message and get AI response"""
    # Get or create conversation
    conversation_id = None
    if message_data.conversation_id:
        conversation_id = uuid.UUID(message_data.conversation_id)
    
    conversation = get_or_create_conversation(db, user_id, conversation_id)
    
    # Save user message
    user_message = create_message(
        db,
        conversation.id,
        role="user",
        content=message_data.content
    )
    
    # Get AI response
    try:
        from core.unified_orchestrator import UnifiedOrchestrator
        
        orchestrator = UnifiedOrchestrator()
        result = orchestrator.process_text_command(
            message_data.content,
            enable_tts=False
        )
        
        ai_response_text = result.get("response", "I'm sorry, I couldn't process that request.")
        actions = result.get("actions", [])
        
        # Format response with action info if needed
        if actions:
            action_summary = f"\n\n[Executed {len(actions)} action(s)]"
            ai_response_text += action_summary
        
    except Exception as e:
        # Fallback response if AI fails
        ai_response_text = f"I encountered an error: {str(e)}. Please try again."
    
    # Save AI response
    assistant_message = create_message(
        db,
        conversation.id,
        role="assistant",
        content=ai_response_text,
        model_used="jarvis-llm-brain"
    )
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.commit()
    
    return user_message, assistant_message


def delete_conversation(
    db: Session,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """Delete a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()
    
    if not conversation:
        return False
    
    db.delete(conversation)
    db.commit()
    return True


def update_message(
    db: Session,
    message_id: uuid.UUID,
    user_id: uuid.UUID,
    content: str
) -> Optional[Message]:
    """Update a message (only user messages can be updated)"""
    message = db.query(Message).join(Conversation).filter(
        Message.id == message_id,
        Conversation.user_id == user_id,
        Message.role == "user"
    ).first()
    
    if not message:
        return None
    
    message.content = content
    db.commit()
    db.refresh(message)
    return message


def delete_message(
    db: Session,
    message_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """Delete a message (only user messages can be deleted)"""
    message = db.query(Message).join(Conversation).filter(
        Message.id == message_id,
        Conversation.user_id == user_id,
        Message.role == "user"
    ).first()
    
    if not message:
        return False
    
    db.delete(message)
    db.commit()
    return True

