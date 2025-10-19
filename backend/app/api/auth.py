from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import httpx
import structlog

from app.core.database import get_db
from app.core.security import create_access_token, generate_guest_id
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.users import User, AuthProvider, UserRole

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)

router = APIRouter()

class GoogleCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

class GuestAuthRequest(BaseModel):
    display_name: str
    user_agent: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/google/callback")
async def google_oauth_callback(
    request: GoogleCallbackRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": request.code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.OAUTH_REDIRECT_URI,
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Get user info
            user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={tokens['access_token']}"
            user_response = await client.get(user_info_url)
            user_response.raise_for_status()
            user_info = user_response.json()
        
        # Find or create user
        result = await db.execute(
            select(User).where(User.email == user_info["email"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                display_name=user_info.get("name", user_info["email"]),
                email=user_info["email"],
                auth_provider=AuthProvider.GOOGLE,
                picture=user_info.get("picture"),  # Google profile picture
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Update picture if it changed
            if user_info.get("picture") and user.picture != user_info.get("picture"):
                user.picture = user_info.get("picture")
                await db.commit()
                await db.refresh(user)
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # Set httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.JWT_EXPIRE_MINUTES * 60
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "display_name": user.display_name,
                "email": user.email,
                "role": user.role.value,
                "auth_provider": user.auth_provider.value,
                "picture": user.picture
            }
        )
        
    except Exception as e:
        logger.error("Google OAuth error", exc_info=e)
        raise HTTPException(status_code=400, detail="Authentication failed")

@router.post("/guest")
async def create_guest_session(
    request: GuestAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Create guest user session"""
    try:
        # Generate guest ID
        guest_id = generate_guest_id(request.user_agent)
        
        # Find or create guest user
        result = await db.execute(
            select(User).where(User.guest_device_hash == guest_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                display_name=request.display_name,
                auth_provider=AuthProvider.GUEST,
                guest_device_hash=guest_id,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": str(user.id), "guest_id": guest_id}
        )
        
        # Set httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,  # Allow for development
            samesite="lax",
            max_age=settings.JWT_EXPIRE_MINUTES * 60
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "display_name": user.display_name,
                "guest_id": guest_id,
                "role": user.role.value,
                "auth_provider": user.auth_provider.value
            }
        )
        
    except Exception as e:
        logger.error("Guest auth error", exc_info=e)
        raise HTTPException(status_code=400, detail="Guest authentication failed")

@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user_info(
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "user": {
            "id": str(current_user.id),
            "display_name": current_user.display_name,
            "email": current_user.email,
            "role": current_user.role.value,
            "auth_provider": current_user.auth_provider.value,
            "picture": current_user.picture
        }
    }