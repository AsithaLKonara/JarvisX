"""
OAuth provider utilities
"""
import httpx
from typing import Optional, Dict
from app.config import settings


async def verify_google_token(token: str) -> Optional[Dict]:
    """Verify Google OAuth token and get user info"""
    if not settings.GOOGLE_CLIENT_ID:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            # Verify token with Google
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture"),
                    "provider_id": user_info.get("id"),
                }
    except Exception:
        pass
    
    return None


async def verify_apple_token(token: str) -> Optional[Dict]:
    """Verify Apple OAuth token and get user info"""
    if not settings.APPLE_CLIENT_ID:
        return None
    
    try:
        # Apple token verification requires more complex flow
        # This is a simplified version - in production, use proper Apple ID verification
        async with httpx.AsyncClient() as client:
            # Note: Apple requires JWT verification with their public keys
            # This is a placeholder - implement proper Apple ID verification
            return {
                "email": None,  # Apple may not provide email
                "name": None,
                "picture": None,
                "provider_id": None,
            }
    except Exception:
        pass
    
    return None


async def verify_facebook_token(token: str) -> Optional[Dict]:
    """Verify Facebook OAuth token and get user info"""
    if not settings.FACEBOOK_CLIENT_ID:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            # Verify token and get user info
            response = await client.get(
                f"https://graph.facebook.com/me",
                params={
                    "access_token": token,
                    "fields": "id,name,email,picture"
                }
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture", {}).get("data", {}).get("url"),
                    "provider_id": user_info.get("id"),
                }
    except Exception:
        pass
    
    return None

