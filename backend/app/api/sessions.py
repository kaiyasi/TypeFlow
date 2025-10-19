from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.sessions import TypingSession, Score
from app.models.articles import Article
from app.models.users import User

router = APIRouter()


class SubmitPayload(BaseModel):
    article_id: UUID4
    article_version: int
    mode_seconds: int
    started_at: datetime
    ended_at: datetime
    language: str
    wpm: float
    accuracy: float
    gross_wpm: Optional[float] = None
    net_wpm: Optional[float] = None
    correct_keystrokes: Optional[int] = None
    error_keystrokes: Optional[int] = None


@router.post("/submit")
async def submit_session(
    payload: SubmitPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Validate article exists
    art_res = await db.execute(select(Article).where(Article.id == payload.article_id))
    article = art_res.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Create session
    session = TypingSession(
        user_id=current_user.id if current_user else None,
        article_id=article.id,
        article_version=payload.article_version,
        mode_seconds=payload.mode_seconds,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Create score
    score = Score(
        session_id=session.id,
        wpm=payload.wpm,
        accuracy=payload.accuracy,
        gross_wpm=payload.gross_wpm or payload.wpm,
        net_wpm=payload.net_wpm or payload.wpm,
        correct_keystrokes=payload.correct_keystrokes or 0,
        error_keystrokes=payload.error_keystrokes or 0,
        language=payload.language,
    )
    db.add(score)
    await db.commit()

    return {"message": "Recorded", "session_id": str(session.id)}
