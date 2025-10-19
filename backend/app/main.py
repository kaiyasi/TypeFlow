from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import structlog
import time
import logging

from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.users import User, UserRole, AuthProvider
from sqlalchemy import select
from app.api import auth, articles, sessions, scores, leaderboard, admin, organizations, config, simple_articles, classrooms, group
from app.ws.router import router as ws_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.LOG_LEVEL.upper())),
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="TypeFlow API",
    description="Advanced Multi-Language Typing Practice Platform",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["typeflow.serelix.xyz", "localhost", "127.0.0.1", "*"]
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "HTTP Request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(simple_articles.router, prefix="/api/simple-articles", tags=["simple-articles"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(scores.router, prefix="/api/scores", tags=["scores"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(classrooms.router, prefix="/api", tags=["classrooms"]) 
app.include_router(group.router, prefix="/api", tags=["group"]) 
app.include_router(organizations.router, prefix="/api/orgs", tags=["organizations"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Include WebSocket router
app.include_router(ws_router, prefix="/ws")

# Add Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "typeflow-api"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TypeFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/healthz"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        method=request.method,
        url=str(request.url)
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Initialize database tables (auto-create for container demo)
@app.on_event("startup")
async def startup_event():
    logger.info("Starting TypeFlow API...")
    # Note: In production, use Alembic for database migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("TypeFlow API started successfully")
    # Promote configured admin emails to SUPER_ADMIN (create if missing)
    try:
        admin_emails = [e.strip() for e in str(settings.ADMIN_EMAIL or "").split(",") if e.strip()]
        if admin_emails:
            async_session = AsyncSessionLocal()
            try:
                for email in admin_emails:
                    res = await async_session.execute(select(User).where(User.email == email))
                    user = res.scalar_one_or_none()
                    if not user:
                        display = email.split("@")[0]
                        user = User(display_name=display, email=email, auth_provider=AuthProvider.GOOGLE, role=UserRole.SUPER_ADMIN)
                        async_session.add(user)
                    else:
                        if user.role != UserRole.SUPER_ADMIN:
                            user.role = UserRole.SUPER_ADMIN
                await async_session.commit()
                logger.info("Admin emails promoted", emails=admin_emails)
            finally:
                await async_session.close()
    except Exception as e:
        logger.error("Failed to promote admin emails", exc_info=e)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down TypeFlow API...")
    await engine.dispose()
    logger.info("TypeFlow API shut down complete")
