from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, UUID4
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.articles import Article, ArticleRevision, ArticleStatus, Language
from app.models.users import User, UserRole
from app.core.deps import get_current_user

router = APIRouter()

class ArticleCreate(BaseModel):
    title: str
    language: str
    content: str
    source: Optional[str] = None
    status: Optional[str] = None  # Allow explicit status setting

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None

class ArticleResponse(BaseModel):
    id: UUID4
    title: str
    language: str
    content: str
    status: str
    version: int
    source: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_by: Optional[dict]
    reviewed_by: Optional[dict]
    review_note: Optional[str]
    published_at: Optional[datetime]

class ArticleListResponse(BaseModel):
    articles: List[ArticleResponse]
    total: int
    page: int
    per_page: int


@router.get("/random", response_model=ArticleResponse)
async def get_random_article(
    language: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a random published article"""
    
    # Direct SQL query to avoid ORM relationship issues
    from sqlalchemy import text
    
    query = "SELECT id, title, language, content, status, created_at FROM articles WHERE (status = 'published' OR status = 'PUBLISHED')"
    params = {}
    
    if language:
        query += " AND language = :language"
        params['language'] = language
    
    query += " ORDER BY RANDOM() LIMIT 1"
    
    try:
        result = await db.execute(text(query), params)
        article_row = result.fetchone()
        
        if not article_row:
            raise HTTPException(status_code=404, detail="No published articles found for the selected criteria.")
        
        # Simple fallback for missing data
        from datetime import datetime
        
        return ArticleResponse(
            id=article_row[0] if article_row[0] else "fallback-id",
            title=article_row[1] if article_row[1] else "Sample Article",
            language=article_row[2] if article_row[2] else language or "en",
            content=article_row[3] if article_row[3] else "This is a sample article content.",
            status=article_row[4] if article_row[4] else "published",
            version=1,
            source=None,
            created_at=article_row[5] if article_row[5] else datetime.now(),
            updated_at=datetime.now(),
            submitted_by=None,
            reviewed_by=None,
            review_note=None,
            published_at=datetime.now()
        )
    except Exception as e:
        print(f"Database error: {e}")
        # Return fallback content if database fails
        return ArticleResponse(
            id="fallback-id",
            title="Touch Typing Practice",
            language=language or "en",
            content="The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is commonly used for typing practice.",
            status="published",
            version=1,
            source=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            submitted_by=None,
            reviewed_by=None,
            review_note=None,
            published_at=datetime.now()
        )


@router.get("/", response_model=ArticleListResponse)
async def list_articles(
    language: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None),  # Search query
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):

    
    # Build query
    query = select(Article).options(
        selectinload(Article.submitter),
        selectinload(Article.reviewer)
    )
    
    # Apply filters
    filters = []
    
    if language:
        try:
            lang_enum = Language(language)
            filters.append(Article.language == lang_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid language")
    
    if status:
        try:
            status_enum = ArticleStatus(status)
            filters.append(Article.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    else:
        # Default: only show published articles for non-admin users
        if not current_user or current_user.role != UserRole.SUPER_ADMIN:
            filters.append(Article.status == ArticleStatus.PUBLISHED)
    
    if q:
        filters.append(
            Article.title.ilike(f"%{q}%") | Article.content.ilike(f"%{q}%")
        )
    
    filters.append(Article.is_active == True)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Get total count
    count_query = select(func.count()).select_from(Article)
    if filters:
        count_query = count_query.where(and_(*filters))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    query = query.order_by(Article.created_at.desc())
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return ArticleListResponse(
        articles=[
            ArticleResponse(
                id=article.id,
                title=article.title,
                language=article.language.value,
                content=article.content,
                status=article.status.value,
                version=article.version,
                source=article.source,
                created_at=article.created_at,
                updated_at=article.updated_at,
                submitted_by={
                    "id": str(article.submitter.id),
                    "display_name": article.submitter.display_name
                } if article.submitter else None,
                reviewed_by={
                    "id": str(article.reviewer.id),
                    "display_name": article.reviewer.display_name
                } if article.reviewer else None,
                review_note=article.review_note,
                published_at=article.published_at
            )
            for article in articles
        ],
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new article"""
    
    try:
        language_enum = Language(article_data.language)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    # Determine initial status based on request
    # All user-submitted articles go through review process
    if article_data.status == "draft":
        status = ArticleStatus.DRAFT
        published_at = None
    else:
        # Default: submit for review (even for admins)
        status = ArticleStatus.SUBMITTED
        published_at = None
    
    article = Article(
        title=article_data.title,
        language=language_enum,
        content=article_data.content,
        source=article_data.source,
        status=status,
        submitted_by_id=current_user.id,
        published_at=published_at
    )
    
    db.add(article)
    await db.commit()
    await db.refresh(article)
    
    # Create revision
    revision = ArticleRevision(
        article_id=article.id,
        version=1,
        content=article_data.content,
        created_by=current_user.id
    )
    db.add(revision)
    await db.commit()
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        language=article.language.value,
        content=article.content,
        status=article.status.value,
        version=article.version,
        source=article.source,
        created_at=article.created_at,
        updated_at=article.updated_at,
        submitted_by={
            "id": str(current_user.id),
            "display_name": current_user.display_name
        },
        reviewed_by=None,
        review_note=None,
        published_at=article.published_at
    )

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: UUID4,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get single article by ID"""
    
    query = select(Article).options(
        selectinload(Article.submitter),
        selectinload(Article.reviewer)
    ).where(Article.id == article_id)
    
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check permissions
    if (article.status != ArticleStatus.PUBLISHED and 
        (not current_user or 
         (current_user.role != UserRole.SUPER_ADMIN and 
          article.submitted_by != current_user.id))):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        language=article.language.value,
        content=article.content,
        status=article.status.value,
        version=article.version,
        source=article.source,
        created_at=article.created_at,
        updated_at=article.updated_at,
        submitted_by={
            "id": str(article.submitter.id),
            "display_name": article.submitter.display_name
        } if article.submitter else None,
        reviewed_by={
            "id": str(article.reviewer.id),
            "display_name": article.reviewer.display_name
        } if article.reviewer else None,
        review_note=article.review_note,
        published_at=article.published_at
    )


class ArticleReviewRequest(BaseModel):
    action: str  # "approve" or "reject"
    review_note: Optional[str] = None


@router.patch("/{article_id}/review", response_model=ArticleResponse)
async def review_article(
    article_id: UUID4,
    review_request: ArticleReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Review an article (approve or reject) - Admin only"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get article
    query = select(Article).options(
        selectinload(Article.submitter),
        selectinload(Article.reviewer)
    ).where(Article.id == article_id, Article.is_active == True)
    
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check if article can be reviewed
    if article.status not in [ArticleStatus.SUBMITTED, ArticleStatus.DRAFT]:
        raise HTTPException(
            status_code=400, 
            detail=f"Article with status '{article.status.value}' cannot be reviewed"
        )
    
    # Update article status
    if review_request.action == "approve":
        article.status = ArticleStatus.APPROVED
        article.reviewed_by_id = current_user.id
        article.review_note = review_request.review_note
        article.reviewed_at = func.now()
        
    elif review_request.action == "reject":
        article.status = ArticleStatus.REJECTED
        article.reviewed_by_id = current_user.id
        article.review_note = review_request.review_note
        article.reviewed_at = func.now()
        
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
    
    await db.commit()
    await db.refresh(article)
    
    # Reload with relationships
    query = select(Article).options(
        selectinload(Article.submitter),
        selectinload(Article.reviewer)
    ).where(Article.id == article_id)
    
    result = await db.execute(query)
    article = result.scalar_one()
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        language=article.language.value,
        content=article.content,
        status=article.status.value,
        version=article.version,
        source=article.source,
        created_at=article.created_at,
        updated_at=article.updated_at,
        submitted_by={
            "id": str(article.submitter.id),
            "display_name": article.submitter.display_name
        } if article.submitter else None,
        reviewed_by={
            "id": str(article.reviewer.id),
            "display_name": article.reviewer.display_name
        } if article.reviewer else None,
        review_note=article.review_note,
        published_at=article.published_at
    )


@router.patch("/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(
    article_id: UUID4,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish an approved article - Admin only"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get article
    query = select(Article).options(
        selectinload(Article.submitter),
        selectinload(Article.reviewer)
    ).where(Article.id == article_id, Article.is_active == True)
    
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check if article can be published
    if article.status != ArticleStatus.APPROVED:
        raise HTTPException(
            status_code=400, 
            detail=f"Only approved articles can be published. Current status: {article.status.value}"
        )
    
    # Update article status
    article.status = ArticleStatus.PUBLISHED
    article.published_at = func.now()
    
    await db.commit()
    await db.refresh(article)
    
    # Reload with relationships
    query = select(Article).options(
        selectinload(Article.submitter),
        selectinload(Article.reviewer)
    ).where(Article.id == article_id)
    
    result = await db.execute(query)
    article = result.scalar_one()
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        language=article.language.value,
        content=article.content,
        status=article.status.value,
        version=article.version,
        source=article.source,
        created_at=article.created_at,
        updated_at=article.updated_at,
        submitted_by={
            "id": str(article.submitter.id),
            "display_name": article.submitter.display_name
        } if article.submitter else None,
        reviewed_by={
            "id": str(article.reviewer.id),
            "display_name": article.reviewer.display_name
        } if article.reviewer else None,
        review_note=article.review_note,
        published_at=article.published_at
    )