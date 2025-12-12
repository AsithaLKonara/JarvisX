"""
User model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class OAuthProvider(str, enum.Enum):
    """OAuth provider types"""
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    
    # OAuth fields
    oauth_provider = Column(Enum(OAuthProvider), nullable=True)
    oauth_id = Column(String(255), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Profile fields
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(String(10), default="true", nullable=False)
    is_verified = Column(String(10), default="false", nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

