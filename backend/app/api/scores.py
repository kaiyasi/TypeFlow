# Placeholder API routes - will be implemented based on requirements

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.users import User, UserRole
from app.models.sessions import Score, TypingSession

router = APIRouter()

class ScoreItem(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    wpm: float
    accuracy: float
    created_at: Optional[str]
    language: Optional[str]

    class Config:
        from_attributes = True


@router.get("/me", response_model=List[ScoreItem])
async def get_my_scores(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取得目前使用者的分數列表"""
    q = (
        select(Score, TypingSession.user_id)
        .join(TypingSession, Score.session_id == TypingSession.id)
        .where(TypingSession.user_id == current_user.id)
        .order_by(Score.created_at.desc())
        .limit(100)
    )
    res = await db.execute(q)
    out: List[ScoreItem] = []
    for s, uid in res.fetchall():
        out.append(ScoreItem(
            id=s.id,
            user_id=uid,
            wpm=float(s.wpm),
            accuracy=float(s.accuracy),
            created_at=s.created_at.isoformat() if s.created_at else None,
            language=s.language,
        ))
    return out

@router.get("/user/{user_id}", response_model=List[ScoreItem])
async def get_user_scores(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取得指定使用者的分數列表（管理員限定）"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    q = (
        select(Score, TypingSession.user_id)
        .join(TypingSession, Score.session_id == TypingSession.id)
        .where(TypingSession.user_id == user_id)
        .order_by(Score.created_at.desc())
        .limit(200)
    )
    res = await db.execute(q)
    out: List[ScoreItem] = []
    for s, uid in res.fetchall():
        out.append(ScoreItem(
            id=s.id,
            user_id=uid,
            wpm=float(s.wpm),
            accuracy=float(s.accuracy),
            created_at=s.created_at.isoformat() if s.created_at else None,
            language=s.language,
        ))
    return out

class ScoreUpdatePayload(BaseModel):
    wpm: Optional[float] = Field(None, ge=0, le=1000)
    accuracy: Optional[float] = Field(None, ge=0, le=100)
    note: Optional[str] = None
    is_void: Optional[bool] = None


@router.patch("/{score_id}")
async def update_score(
    score_id: UUID,
    payload: ScoreUpdatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新分數（僅管理員）"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")

    res = await db.execute(select(Score).where(Score.id == score_id))
    s: Optional[Score] = res.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Score not found")

    if payload.wpm is not None:
        s.wpm = float(payload.wpm)
        # 同步 net_wpm/gross_wpm，若需要更精準可另計
        s.net_wpm = float(payload.wpm)
    if payload.accuracy is not None:
        s.accuracy = float(payload.accuracy)
    if payload.note is not None:
        s.note = payload.note
    if payload.is_void is not None:
        s.is_void = bool(payload.is_void)

    await db.commit()
    return {"message": "Score updated"}
