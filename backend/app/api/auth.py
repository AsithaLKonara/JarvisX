"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.auth import UserCreate, UserLogin, OAuthLogin, Token, UserResponse
from app.services.auth_service import (
    create_user,
    authenticate_user,
    authenticate_oauth_user,
    create_tokens,
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        user = create_user(db, user_data)
        tokens = create_tokens(user)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = create_tokens(user)
    return tokens


@router.post("/oauth", response_model=Token)
async def oauth_login(oauth_data: OAuthLogin, db: Session = Depends(get_db)):
    """Login with OAuth provider"""
    user = await authenticate_oauth_user(db, oauth_data.provider, oauth_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OAuth token or provider",
        )
    
    tokens = create_tokens(user)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    from app.utils.jwt import verify_token
    
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    tokens = create_tokens(user)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    from app.schemas.user import UserResponse
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified == "true",
        created_at=current_user.created_at.isoformat(),
    )

