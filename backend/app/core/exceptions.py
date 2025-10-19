"""
自訂例外處理
"""
from fastapi import HTTPException, status


class TypeFlowException(Exception):
    """基礎例外類別"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(TypeFlowException):
    """認證錯誤"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(TypeFlowException):
    """授權錯誤"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(TypeFlowException):
    """資源未找到"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class ValidationError(TypeFlowException):
    """驗證錯誤"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class DuplicateError(TypeFlowException):
    """重複資源錯誤"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} already exists", status.HTTP_409_CONFLICT)


class RateLimitError(TypeFlowException):
    """速率限制錯誤"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class DatabaseError(TypeFlowException):
    """資料庫錯誤"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


# HTTP 例外快捷方式
def http_401(detail: str = "Not authenticated"):
    """401 未認證"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def http_403(detail: str = "Permission denied"):
    """403 禁止訪問"""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def http_404(detail: str = "Not found"):
    """404 未找到"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def http_422(detail: str = "Validation error"):
    """422 驗證錯誤"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail,
    )


def http_429(detail: str = "Too many requests"):
    """429 請求過多"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail,
    )


def http_500(detail: str = "Internal server error"):
    """500 伺服器錯誤"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
    )

