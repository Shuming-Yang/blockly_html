# project_validator.py
import json
import hmac
import hashlib
from typing import Any, Dict

class ProjectValidator:
    # 隱藏的金鑰日期
    INTERNAL_KEY_DATE = "2026-04-07"

    @classmethod
    def generate_signature(cls, data: Dict[str, Any]) -> str:
        """
        核心演算法: HMAC-SHA256
        功能: 純粹計算並回傳驗證碼字串, 不修改原始資料
        """
        try:
            # 1. 準備資料: 排除「驗證碼」欄位本身
            data_copy = {k: v for k, v in data.items() if k != 'verification_code'}
            
            # 2. 序列化
            content_str = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
            
            # 3. HMAC 計算
            key_bytes = f"Omnivision{cls.INTERNAL_KEY_DATE}".encode('utf-8')
            message_bytes = content_str.encode('utf-8')
            
            return hmac.new(
                key_bytes, 
                msg=message_bytes, 
                digestmod=hashlib.sha256
            ).hexdigest().upper()
        except Exception:
            return ""

    @classmethod
    def verify(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        功能: 驗證專案的 verification_code 是否正確
        """
        try:
            if 'verification_code' not in data:
                return {"valid": False, "reason": "Missing verification code."}
            
            # 重新計算正確驗證碼
            expected = cls.generate_signature(data)
            
            # 安全比對
            if hmac.compare_digest(data['verification_code'], expected):
                return {"valid": True}
            else:
                return {"valid": False, "reason": "Verification code invalid. File might be modified."}
        except Exception as e:
            return {"valid": False, "reason": str(e)}
