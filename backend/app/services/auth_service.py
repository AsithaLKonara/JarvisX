"""
Authentication service
"""
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User, OAuthProvider
from app.utils.jwt import create_access_token, create_refresh_token
from app.utils.oauth import verify_google_token, verify_apple_token, verify_facebook_token
from app.schemas.auth import UserCreate, UserLogin, OAuthLogin, Token
import uuid

# Password hashing - use pbkdf2_sha256 for compatibility
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Create user
    user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        username=user_data.username or user_data.email.split("@")[0],
        password_hash=get_password_hash(user_data.password),
        is_active="true",
        is_verified="false",
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if not user.password_hash:
        return None  # OAuth-only user
    
    if not verify_password(password, user.password_hash):
        return None
    
    if user.is_active != "true":
        return None
    
    return user


async def authenticate_oauth_user(
    db: Session,
    provider: str,
    token: str
) -> Optional[User]:
    """Authenticate user via OAuth"""
    # Verify token with provider
    user_info = None
    
    if provider == "google":
        user_info = await verify_google_token(token)
        oauth_provider = OAuthProvider.GOOGLE
    elif provider == "apple":
        user_info = await verify_apple_token(token)
        oauth_provider = OAuthProvider.APPLE
    elif provider == "facebook":
        user_info = await verify_facebook_token(token)
        oauth_provider = OAuthProvider.FACEBOOK
    else:
        return None
    
    if not user_info or not user_info.get("provider_id"):
        return None
    
    # Find or create user
    user = db.query(User).filter(
        User.oauth_provider == oauth_provider,
        User.oauth_id == user_info["provider_id"]
    ).first()
    
    if not user:
        # Create new OAuth user
        user = User(
            id=uuid.uuid4(),
            email=user_info.get("email") or f"{provider}_{user_info['provider_id']}@oauth.local",
            username=user_info.get("name") or user_info["provider_id"],
            password_hash=None,
            oauth_provider=oauth_provider,
            oauth_id=user_info["provider_id"],
            avatar_url=user_info.get("picture"),
            is_active="true",
            is_verified="true" if user_info.get("email") else "false",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user info
        if user_info.get("email") and not user.email.startswith(provider):
            user.email = user_info["email"]
        if user_info.get("name"):
            user.username = user_info["name"]
        if user_info.get("picture"):
            user.avatar_url = user_info["picture"]
        db.commit()
        db.refresh(user)
    
    return user


def create_tokens(user: User) -> Token:
    """Create access and refresh tokens for user"""
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

