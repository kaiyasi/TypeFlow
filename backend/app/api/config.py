from fastapi import APIRouter, Depends
from pydantic import BaseModel
import structlog

from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.users import User
from app.models.articles import Article, ArticleStatus

router = APIRouter()
logger = structlog.get_logger()

class AppConfig(BaseModel):
    google_client_id: str

@router.get("/", response_model=AppConfig)
async def get_app_config():
    """Provide public client-side application configuration."""
    logger.info("Serving app config", google_client_id=settings.GOOGLE_CLIENT_ID)
    return AppConfig(
        google_client_id=settings.GOOGLE_CLIENT_ID
    )


class PublicStats(BaseModel):
    totalUsers: int
    totalArticles: int
    totalRecords: int


@router.get("/public-stats", response_model=PublicStats)
async def get_public_stats(db: AsyncSession = Depends(get_db)):
    """Public, lightweight counts for homepage counters."""
    # Users count
    users_q = select(func.count()).select_from(User)
    users_res = await db.execute(users_q)
    total_users = users_res.scalar() or 0

    # Published articles count
    articles_q = select(func.count()).select_from(Article).where(
        Article.status == ArticleStatus.PUBLISHED,
        Article.is_active == True,
    )
    art_res = await db.execute(articles_q)
    total_articles = art_res.scalar() or 0

    # Typing records not implemented yet
    return PublicStats(
        totalUsers=total_users,
        totalArticles=total_articles,
        totalRecords=0,
    )
