"""
安全中間件
"""
from fastapi import Request
from fastapi.responses import Response
from typing import Callable
import re


async def security_headers_middleware(request: Request, call_next: Callable):
    """添加安全 headers"""
    response: Response = await call_next(request)
    
    # 安全 headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' ws: wss:;"
    )
    
    # 移除可能洩漏伺服器信息的 headers
    response.headers.pop("Server", None)
    response.headers.pop("X-Powered-By", None)
    
    return response


async def input_sanitization_middleware(request: Request, call_next: Callable):
    """輸入清理中間件"""
    # 檢查常見的攻擊模式
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',                 # JavaScript 協議
        r'on\w+\s*=',                  # 事件處理器
        r'DROP\s+TABLE',                # SQL Injection
        r'UNION\s+SELECT',              # SQL Injection
        r'\.\./\.\.',                   # Path Traversal
    ]
    
    # 檢查 URL
    for pattern in dangerous_patterns:
        if re.search(pattern, str(request.url), re.IGNORECASE):
            return Response(
                content="Malicious input detected",
                status_code=400
            )
    
    # 檢查 query 參數
    for key, value in request.query_params.items():
        for pattern in dangerous_patterns:
            if re.search(pattern, str(value), re.IGNORECASE):
                return Response(
                    content="Malicious input detected in query parameters",
                    status_code=400
                )
    
    response = await call_next(request)
    return response


def validate_content_type(request: Request) -> bool:
    """驗證 Content-Type"""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        allowed_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ]
        return any(ct in content_type for ct in allowed_types)
    return True


async def content_type_validation_middleware(request: Request, call_next: Callable):
    """Content-Type 驗證中間件"""
    if not validate_content_type(request):
        return Response(
            content="Invalid content type",
            status_code=415
        )
    
    response = await call_next(request)
    return response


# CSRF 保護
class CSRFProtection:
    """CSRF 保護類別"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self, session_id: str) -> str:
        """生成 CSRF token"""
        import hmac
        import hashlib
        
        return hmac.new(
            self.secret_key.encode(),
            session_id.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """驗證 CSRF token"""
        expected_token = self.generate_token(session_id)
        return hmac.compare_digest(token, expected_token)


# IP 白名單/黑名單
class IPFilter:
    """IP 過濾器"""
    
    def __init__(self):
        self.whitelist = set()
        self.blacklist = set()
    
    def add_to_whitelist(self, ip: str):
        """添加到白名單"""
        self.whitelist.add(ip)
    
    def add_to_blacklist(self, ip: str):
        """添加到黑名單"""
        self.blacklist.add(ip)
    
    def is_allowed(self, ip: str) -> bool:
        """檢查 IP 是否允許"""
        if ip in self.blacklist:
            return False
        if self.whitelist and ip not in self.whitelist:
            return False
        return True


ip_filter = IPFilter()


async def ip_filter_middleware(request: Request, call_next: Callable):
    """IP 過濾中間件"""
    client_ip = request.client.host
    
    if not ip_filter.is_allowed(client_ip):
        return Response(
            content="Access denied",
            status_code=403
        )
    
    response = await call_next(request)
    return response

