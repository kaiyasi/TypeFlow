"""
API 限流中間件
"""
import time
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from app.core.config import settings

# 初始化 Redis 連線
redis_client = None

async def get_redis_client():
    """獲取 Redis 客戶端"""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


class RateLimiter:
    """限流器類別"""
    
    def __init__(
        self,
        times: int = 60,
        seconds: int = 60,
        identifier: str = "ip"
    ):
        """
        初始化限流器
        
        Args:
            times: 允許的請求次數
            seconds: 時間窗口（秒）
            identifier: 識別方式 (ip 或 user)
        """
        self.times = times
        self.seconds = seconds
        self.identifier = identifier
    
    async def __call__(self, request: Request, call_next: Callable):
        """限流檢查"""
        # 獲取識別碼
        if self.identifier == "ip":
            key = f"rate_limit:ip:{request.client.host}"
        elif self.identifier == "user":
            # 從 token 中獲取用戶 ID
            auth = request.headers.get("Authorization")
            if auth and auth.startswith("Bearer "):
                token = auth.split(" ")[1]
                key = f"rate_limit:user:{token[:10]}"
            else:
                key = f"rate_limit:ip:{request.client.host}"
        else:
            key = f"rate_limit:ip:{request.client.host}"
        
        # 檢查限流
        redis = await get_redis_client()
        
        # 獲取當前計數
        count = await redis.get(key)
        
        if count is None:
            # 首次請求，設定計數和過期時間
            await redis.setex(key, self.seconds, 1)
        else:
            count = int(count)
            if count >= self.times:
                # 超過限制
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many requests. Please try again later.",
                        "retry_after": self.seconds
                    }
                )
            # 增加計數
            await redis.incr(key)
        
        # 繼續處理請求
        response = await call_next(request)
        
        # 添加限流信息到 header
        response.headers["X-RateLimit-Limit"] = str(self.times)
        response.headers["X-RateLimit-Remaining"] = str(
            self.times - (int(count) if count else 1)
        )
        
        return response


async def rate_limit_middleware(request: Request, call_next: Callable):
    """全局限流中間件"""
    limiter = RateLimiter(
        times=settings.RATE_LIMIT_PER_MIN,
        seconds=60,
        identifier="ip"
    )
    return await limiter(request, call_next)


# 裝飾器版本的限流器
def rate_limit(times: int = 60, seconds: int = 60):
    """
    限流裝飾器
    
    Usage:
        @app.get("/api/endpoint")
        @rate_limit(times=10, seconds=60)
        async def endpoint():
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 檢查限流邏輯
            return await func(*args, **kwargs)
        return wrapper
    return decorator

