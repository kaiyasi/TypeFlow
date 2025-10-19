from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.users import User, UserRole
from app.models.articles import Article, ArticleStatus, Language, ArticleRevision

router = APIRouter()


# Response models
class ArticleListItem(BaseModel):
    id: UUID
    title: str
    content: str
    language: str
    difficulty: Optional[str] = None
    status: str
    author_name: str
    created_at: str

    class Config:
        from_attributes = True


class UserListItem(BaseModel):
    id: UUID
    email: Optional[str]
    display_name: str
    picture: Optional[str]
    role: str
    created_at: str
    record_count: int = 0

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    pendingArticles: int
    approvedArticles: int
    totalUsers: int
    totalRecords: int


class RoleUpdate(BaseModel):
    role: str  # one of: user, org_admin, super_admin


class RoleUpdateByEmail(BaseModel):
    email: str
    role: str  # one of: user, org_admin, super_admin


@router.get("/stats", response_model=StatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get admin dashboard statistics"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Count pending articles
    pending_query = select(func.count()).select_from(Article).where(
        Article.status == ArticleStatus.SUBMITTED,
        Article.is_active == True
    )
    pending_result = await db.execute(pending_query)
    pending_count = pending_result.scalar()

    # Count approved articles
    approved_query = select(func.count()).select_from(Article).where(
        Article.status == ArticleStatus.APPROVED,
        Article.is_active == True
    )
    approved_result = await db.execute(approved_query)
    approved_count = approved_result.scalar()

    # Count total users
    users_query = select(func.count()).select_from(User)
    users_result = await db.execute(users_query)
    users_count = users_result.scalar()

    # TODO: Implement total records count from typing_records table

    return StatsResponse(
        pendingArticles=pending_count,
        approvedArticles=approved_count,
        totalUsers=users_count,
        totalRecords=0
    )


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None  # Language enum value
    status: Optional[str] = None    # ArticleStatus enum value


@router.put("/articles/{article_id}")
async def update_article(
    article_id: UUID,
    payload: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an article (admin only). Creates a revision if content changes."""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.execute(select(Article).where(Article.id == article_id, Article.is_active == True))
    article: Optional[Article] = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Track if content changes to create revision
    content_changed = False

    if payload.title is not None:
        article.title = payload.title

    if payload.content is not None and payload.content != article.content:
        content_changed = True
        # Create a revision before overwriting
        rev = ArticleRevision(
            article_id=article.id,
            version=article.version,
            content=article.content,
            created_by=current_user.id,
        )
        db.add(rev)
        article.content = payload.content
        article.version = article.version + 1

    if payload.language is not None:
        try:
            article.language = Language(payload.language)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid language value")

    if payload.status is not None:
        try:
            new_status = ArticleStatus(payload.status)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid status value")
        article.status = new_status

    await db.commit()

    return {
        "message": "Article updated successfully",
        "content_revision_created": content_changed,
        "version": article.version,
    }


@router.get("/articles/pending")
async def get_pending_articles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get articles pending review"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = select(Article).options(
        selectinload(Article.submitter)
    ).where(
        Article.status == ArticleStatus.SUBMITTED,
        Article.is_active == True
    ).order_by(Article.created_at.desc())

    result = await db.execute(query)
    articles = result.scalars().all()

    return [
        {
            "id": str(article.id),
            "title": article.title,
            "content": article.content,
            "language": article.language.value,
            "difficulty": None,  # Add if you have difficulty field
            "status": article.status.value,
            "author_name": article.submitter.display_name if article.submitter else "Unknown",
            "created_at": article.created_at.isoformat()
        }
        for article in articles
    ]


@router.get("/articles")
async def get_all_articles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all articles (admin view)"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = select(Article).options(
        selectinload(Article.submitter)
    ).where(
        Article.is_active == True
    ).order_by(Article.created_at.desc())

    result = await db.execute(query)
    articles = result.scalars().all()

    return [
        {
            "id": str(article.id),
            "title": article.title,
            "content": article.content,
            "language": article.language.value,
            "difficulty": None,
            "status": article.status.value,
            "author_name": article.submitter.display_name if article.submitter else "Unknown",
            "created_at": article.created_at.isoformat()
        }
        for article in articles
    ]


@router.post("/articles/{article_id}/approve")
async def approve_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve an article"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = select(Article).where(Article.id == article_id, Article.is_active == True)
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.status not in [ArticleStatus.SUBMITTED, ArticleStatus.DRAFT]:
        raise HTTPException(
            status_code=400,
            detail=f"Article with status '{article.status.value}' cannot be approved"
        )

    article.status = ArticleStatus.PUBLISHED
    article.reviewed_by_id = current_user.id
    article.reviewed_at = func.now()
    article.published_at = func.now()

    await db.commit()

    return {"message": "Article approved successfully"}


@router.post("/articles/{article_id}/reject")
async def reject_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject an article"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = select(Article).where(Article.id == article_id, Article.is_active == True)
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.status not in [ArticleStatus.SUBMITTED, ArticleStatus.DRAFT]:
        raise HTTPException(
            status_code=400,
            detail=f"Article with status '{article.status.value}' cannot be rejected"
        )

    article.status = ArticleStatus.REJECTED
    article.reviewed_by_id = current_user.id
    article.reviewed_at = func.now()

    await db.commit()

    return {"message": "Article rejected successfully"}


@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an article (soft delete)"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = select(Article).where(Article.id == article_id, Article.is_active == True)
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_active = False
    await db.commit()

    return {"message": "Article deleted successfully"}


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = select(User).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return [
        {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "picture": user.picture,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "record_count": 0  # TODO: Implement actual count
        }
        for user in users
    ]


@router.post("/users/{user_id}/role")
async def set_user_role(
    user_id: UUID,
    payload: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a user's role (SUPER_ADMIN only)."""
    # Only SUPER_ADMIN can change roles
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin access required")

    # Validate role
    try:
        new_role = UserRole(payload.role)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid role value")

    # Prevent locking yourself out by demoting self
    if user_id == current_user.id and new_role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    await db.commit()

    return {"message": "Role updated", "user_id": str(user.id), "role": user.role.value}


@router.post("/users/by-email/role")
async def set_user_role_by_email(
    payload: RoleUpdateByEmail,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a user's role by email (SUPER_ADMIN only). If user does not exist, create and assign role."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin access required")

    # Validate role
    try:
        new_role = UserRole(payload.role)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid role value")

    # Prevent changing own role by email
    if current_user.email and payload.email.strip().lower() == current_user.email.lower() and new_role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    email = payload.email.strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        # Create minimal user record if not exists
        display = email.split("@")[0]
        user = User(display_name=display, email=email, auth_provider=AuthProvider.GOOGLE, role=new_role)
        db.add(user)
    else:
        user.role = new_role

    await db.commit()

    return {"message": "Role set", "email": email, "role": new_role.value}
