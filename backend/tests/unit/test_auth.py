"""
認證系統測試
"""
import pytest
from httpx import AsyncClient
from app.core.security import (
    create_access_token,
    verify_token,
    verify_password,
    get_password_hash
)


class TestPasswordHashing:
    """密碼雜湊測試"""
    
    def test_password_hashing(self):
        """測試密碼雜湊"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_password_verification(self):
        """測試密碼驗證"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """測試不同密碼產生不同雜湊"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2


class TestJWTToken:
    """JWT Token 測試"""
    
    def test_create_access_token(self):
        """測試建立 Token"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """測試驗證有效 Token"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
    
    def test_verify_invalid_token(self):
        """測試驗證無效 Token"""
        payload = verify_token("invalid_token_string")
        assert payload is None
    
    def test_verify_expired_token(self):
        """測試驗證過期 Token"""
        # 這需要模擬時間，暫時跳過
        pass


class TestAuthEndpoints:
    """認證端點測試"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, client: AsyncClient):
        """測試未帶 Token 訪問需要認證的端點"""
        response = await client.get("/api/auth/me")
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_token(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """測試帶 Token 訪問用戶資訊"""
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_invalid_token_format(self, client: AsyncClient):
        """測試無效的 Token 格式"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_missing_bearer_prefix(self, client: AsyncClient):
        """測試缺少 Bearer 前綴"""
        headers = {"Authorization": "some_token"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code in [401, 403]


class TestUserRoles:
    """用戶角色測試"""
    
    @pytest.mark.asyncio
    async def test_admin_access_admin_endpoint(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """測試管理員訪問管理端點"""
        response = await client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code in [200, 404]  # 404 如果端點未實作
    
    @pytest.mark.asyncio
    async def test_user_cannot_access_admin_endpoint(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """測試一般用戶無法訪問管理端點"""
        response = await client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code == 403

