from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_token
from app.models.users import User

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(security)
) -> Optional[User]:
    """Get current user from JWT token (optional)"""
    
    # Try to get token from cookie first
    auth_cookie = request.cookies.get("access_token")
    if auth_cookie and auth_cookie.startswith("Bearer "):
        token_value = auth_cookie[7:]  # Remove "Bearer " prefix
    elif token:
        token_value = token.credentials
    else:
        return None
    
    # Verify token
    payload = verify_token(token_value)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    return user

async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Get current user (required - raises 401 if not authenticated)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user