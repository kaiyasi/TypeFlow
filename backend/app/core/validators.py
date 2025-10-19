"""
資料驗證工具
"""
import re
from typing import Optional
from pydantic import validator, BaseModel


def validate_email(email: str) -> bool:
    """驗證電子郵件格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    驗證密碼強度
    
    要求:
    - 至少 8 個字符
    - 至少一個大寫字母
    - 至少一個小寫字母
    - 至少一個數字
    """
    if len(password) < 8:
        return False, "密碼至少需要 8 個字符"
    
    if not re.search(r'[A-Z]', password):
        return False, "密碼需要至少一個大寫字母"
    
    if not re.search(r'[a-z]', password):
        return False, "密碼需要至少一個小寫字母"
    
    if not re.search(r'\d', password):
        return False, "密碼需要至少一個數字"
    
    return True, "密碼強度足夠"


def validate_username(username: str) -> tuple[bool, str]:
    """
    驗證用戶名
    
    要求:
    - 3-50 個字符
    - 只能包含字母、數字、底線、連字符
    """
    if len(username) < 3:
        return False, "用戶名至少需要 3 個字符"
    
    if len(username) > 50:
        return False, "用戶名最多 50 個字符"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "用戶名只能包含字母、數字、底線和連字符"
    
    return True, "用戶名有效"


def validate_wpm(wpm: float) -> tuple[bool, str]:
    """
    驗證 WPM 是否在合理範圍內
    
    人類打字速度極限約 200 WPM
    """
    if wpm < 0:
        return False, "WPM 不能為負數"
    
    if wpm > 300:
        return False, "WPM 超過人類極限，可能存在作弊"
    
    if wpm > 200:
        return True, "WPM 異常高，需要進一步審查"
    
    return True, "WPM 正常"


def validate_accuracy(accuracy: float) -> tuple[bool, str]:
    """驗證準確度是否在有效範圍內"""
    if accuracy < 0 or accuracy > 100:
        return False, "準確度必須在 0-100 之間"
    
    return True, "準確度有效"


def validate_typing_session(
    wpm: float,
    accuracy: float,
    duration: int
) -> tuple[bool, str]:
    """
    驗證打字會話的合理性
    
    檢測可能的作弊行為:
    - WPM 超過 200
    - 高速度配合超高準確度
    - 時長異常
    """
    # 檢查 WPM
    wpm_valid, wpm_msg = validate_wpm(wpm)
    if not wpm_valid:
        return False, wpm_msg
    
    # 檢查準確度
    acc_valid, acc_msg = validate_accuracy(accuracy)
    if not acc_valid:
        return False, acc_msg
    
    # 檢查時長
    if duration <= 0:
        return False, "時長必須大於 0"
    
    if duration > 3600:
        return False, "時長不能超過 1 小時"
    
    # 檢查異常組合
    if wpm > 150 and accuracy > 98:
        return False, "高速度配合超高準確度，可疑"
    
    if wpm > 200:
        return False, "WPM 超過人類極限"
    
    return True, "打字會話數據有效"


def sanitize_html(text: str) -> str:
    """清理 HTML 標籤防止 XSS"""
    # 簡單的 HTML 標籤移除
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text


def validate_article_content(content: str) -> tuple[bool, str]:
    """驗證文章內容"""
    if not content or len(content.strip()) == 0:
        return False, "文章內容不能為空"
    
    if len(content) < 50:
        return False, "文章內容至少需要 50 個字符"
    
    if len(content) > 50000:
        return False, "文章內容不能超過 50000 個字符"
    
    return True, "文章內容有效"


def validate_language_code(language: str) -> bool:
    """驗證語言代碼"""
    valid_languages = ["en", "code", "zh-TW", "zh-CN", "ja", "ko", "de", "ru"]
    return language in valid_languages


class PaginationParams(BaseModel):
    """分頁參數"""
    page: int = 1
    page_size: int = 20
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('頁碼必須大於 0')
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1:
            raise ValueError('每頁數量必須大於 0')
        if v > 100:
            raise ValueError('每頁數量不能超過 100')
        return v

