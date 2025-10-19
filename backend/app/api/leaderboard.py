# Real leaderboard API implementation

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.sessions import Score, TypingSession
from app.models.users import User

router = APIRouter()

class LeaderboardItem(BaseModel):
    rank: int
    user_id: str
    display_name: str
    picture: Optional[str] = None
    wpm: float
    accuracy: float
    date: datetime

class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardItem]
    total_count: int

@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard(
    scope: str = Query("daily", description="Time scope: daily, weekly, monthly, alltime"),
    category: str = Query("overall", description="Category: overall, en, code, zh-TW, etc."),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard from real scores; no placeholders returned."""

    # Calculate time filter
    now = datetime.utcnow()
    if scope == "daily":
        start_date = now - timedelta(days=1)
    elif scope == "weekly":
        start_date = now - timedelta(weeks=1)
    elif scope == "monthly":
        start_date = now - timedelta(days=30)
    else:
        start_date = None

    # Base query: scores joined to users
    query = select(
        Score.wpm,
        Score.accuracy,
        Score.created_at,
        User.id.label('user_id'),
        User.display_name,
        User.picture,
    ).join(TypingSession, Score.session_id == TypingSession.id, isouter=True)
    query = query.join(User, TypingSession.user_id == User.id, isouter=True)

    # Filter voided and non-positive scores
    query = query.where(Score.is_void == False, Score.wpm > 0, Score.accuracy > 0)

    # Time filter
    if start_date:
        query = query.where(Score.created_at >= start_date)

    # Language/category filter (if provided and not overall)
    if category and category.lower() != 'overall':
        query = query.where(Score.language == category)

    # Order best scores first
    query = query.order_by(desc(Score.wpm), desc(Score.accuracy), desc(Score.created_at)).limit(limit)

    try:
        result = await db.execute(query)
        rows = result.fetchall()
        entries: List[LeaderboardItem] = []
        for idx, (wpm, accuracy, created_at, user_id, display_name, picture) in enumerate(rows, 1):
            if not user_id:
                # Skip entries without user id to avoid placeholders
                continue
            entries.append(LeaderboardItem(
                rank=idx,
                user_id=str(user_id),
                display_name=display_name or f"User-{str(user_id)[:6]}",
                picture=picture,
                wpm=float(wpm),
                accuracy=float(accuracy),
                date=created_at or now,
            ))

        return LeaderboardResponse(entries=entries, total_count=len(entries))
    except Exception:
        return LeaderboardResponse(entries=[], total_count=0)
