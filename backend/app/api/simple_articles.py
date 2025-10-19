from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import get_db

router = APIRouter()

class SimpleArticleResponse(BaseModel):
    id: str
    title: str
    language: str
    content: str

@router.get("/random")
async def get_random_article_simple(
    language: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a random published article - simplified version"""
    
    # Define fallback content for different languages
    fallback_content = {
        "en": {
            "title": "Touch Typing Practice",
            "content": "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is commonly used for typing practice. Regular practice helps improve both speed and accuracy in typing skills."
        },
        "zh-TW": {
            "title": "打字練習",
            "content": "敏捷的棕色狐狸跳過懶惰的狗。這句話包含了英文字母表中的每個字母，通常用於打字練習。定期練習有助於提高打字技能的速度和準確性。中文打字需要熟悉注音符號或其他輸入法。"
        },
        "code": {
            "title": "JavaScript Code Practice",
            "content": "function calculateSum(a, b) {\n    return a + b;\n}\n\nconst numbers = [1, 2, 3, 4, 5];\nconst total = numbers.reduce((sum, num) => sum + num, 0);\nconsole.log('Total sum:', total);\n\nif (total > 10) {\n    console.log('Sum is greater than 10');\n}"
        }
    }
    
    # Try to get from database first
    try:
        query = "SELECT id, title, language, content FROM articles WHERE (status = 'published' OR status = 'PUBLISHED')"
        params = {}
        
        if language:
            query += " AND language = :language"
            params['language'] = language
        
        query += " ORDER BY RANDOM() LIMIT 1"
        
        result = await db.execute(text(query), params)
        article_row = result.fetchone()
        
        if article_row:
            return SimpleArticleResponse(
                id=str(article_row[0]),
                title=article_row[1],
                language=article_row[2],
                content=article_row[3]
            )
    except Exception as e:
        print(f"Database query failed: {e}")
    
    # Use fallback content
    lang = language or "en"
    if lang not in fallback_content:
        lang = "en"
    
    content = fallback_content[lang]
    
    return SimpleArticleResponse(
        id="fallback-" + lang,
        title=content["title"],
        language=lang,
        content=content["content"]
    )