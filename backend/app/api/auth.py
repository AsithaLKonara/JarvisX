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
async def refresh_token(
    refresh_token_data: dict,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    from app.utils.jwt import verify_token
    from pydantic import BaseModel
    
    class RefreshTokenRequest(BaseModel):
        refresh_token: str
    
    # Handle both dict and request body
    if isinstance(refresh_token_data, dict):
        refresh_token_str = refresh_token_data.get("refresh_token")
    else:
        refresh_token_str = refresh_token_data.refresh_token
    
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required",
        )
    
    payload = verify_token(refresh_token_str, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    import uuid
    user_id = uuid.UUID(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    tokens = create_tokens(user)
    return tokens


@router.post("/forgot-password")
async def forgot_password(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    email = request_data.get("email") if isinstance(request_data, dict) else request_data
    
    # TODO: Implement password reset email sending
    user = db.query(User).filter(User.email == email).first()
    
    # Always return success to prevent email enumeration
    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/reset-password")
async def reset_password(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    from app.utils.jwt import verify_token
    from app.services.auth_service import get_password_hash
    
    token = request_data.get("token") if isinstance(request_data, dict) else request_data.get("token")
    new_password = request_data.get("new_password") if isinstance(request_data, dict) else request_data.get("new_password")
    
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and new_password are required",
        )
    
    # TODO: Verify reset token (should be different from refresh token)
    payload = verify_token(token, token_type="reset")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    import uuid
    user_id = uuid.UUID(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password reset successfully"}


@router.post("/verify-email")
async def verify_email(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Verify email address"""
    from app.utils.jwt import verify_token
    
    token = request_data.get("token") if isinstance(request_data, dict) else request_data
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is required",
        )
    
    payload = verify_token(token, token_type="email_verification")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    import uuid
    user_id = uuid.UUID(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_verified = "true"
    db.commit()
    
    return {"message": "Email verified successfully"}


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

