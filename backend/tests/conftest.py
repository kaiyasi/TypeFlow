"""
測試配置和共用 fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.users import User, UserRole, AuthProvider
from app.core.security import get_password_hash, create_access_token

# 測試資料庫 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 建立測試引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """建立事件迴圈"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """建立資料庫會話"""
    # 建立所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 建立會話
    async with TestSessionLocal() as session:
        yield session
    
    # 清理所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """建立測試客戶端"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """建立測試用戶"""
    user = User(
        display_name="Test User",
        email="test@example.com",
        auth_provider=AuthProvider.GOOGLE,
        role=UserRole.USER,
        password_hash=get_password_hash("testpassword123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession) -> User:
    """建立測試管理員"""
    admin = User(
        display_name="Admin User",
        email="admin@example.com",
        auth_provider=AuthProvider.GOOGLE,
        role=UserRole.SUPER_ADMIN,
        password_hash=get_password_hash("adminpassword123")
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user: User) -> str:
    """生成用戶 Token"""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """生成管理員 Token"""
    return create_access_token(data={"sub": str(test_admin.id)})


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """生成認證 headers"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """生成管理員認證 headers"""
    return {"Authorization": f"Bearer {admin_token}"}

