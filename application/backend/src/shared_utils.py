# shared_utils.py
"""
專門提供給後端模組使用的共享工具涵式

Author: OVT AE
Date: 2026-03-04
Description:
    提供跨模組共用的底層工具與演算法, 包含執行緒安全的日誌紀錄器與二進位資料校驗碼計算.
"""
import threading
from datetime import datetime
from typing import Any

_lock = threading.Lock()

def global_log(tag: str, message: Any) -> None:
    """
    執行緒安全的系統日誌紀錄器.
    具備 Python 直譯器關閉 (Shutdown) 期間的全域變數銷毀防護, 避免在程式生命週期終點引發 AttributeError.
    """
    ts = "UNKNOWN_TIME"
    try:
        # 獲取高精度時間戳, 供多執行緒環境下的時序追蹤使用
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    except (AttributeError, TypeError, ImportError, NameError):
        # 防禦 Python 直譯器結束時將 datetime 模組指標設為 None 的極端情況
        ts = "SHUTDOWN_TIME"
    except Exception:
        ts = "ERROR_TIME"
    with _lock:
        try:
            # 確保多執行緒併發寫入時, 終端機輸出不會發生字串交錯或斷行異常
            print(f"[{ts}][{tag:>16}] {message}", flush=True)
        except ValueError:
            # 防禦標準輸出串流 (stdout) 已被底層作業系統強制回收關閉的情況
            pass

def crc_16(data: bytes) -> int:
    """
    計算二進位資料的 CRC-16 校驗碼.
    採用 CCITT 標準多項式 (Polynomial 0x1021) 進行嚴格的位元運算, 確保硬體端能正確驗證資料流完整性.
    """
    crc = 0xFFFF  # 初始化 CRC 預設值
    POLYNOMIAL = 0x1021  # 定義 CCITT 標準多項式
    # 遍歷所有 byte 與 bit 進行 XOR 與位移運算
    for c in data:
        # 將當前 byte 移至高位元並與 CRC 暫存器進行 XOR 混淆
        crc = crc ^ (c << 8)
        for _ in range(8):
            # 針對每一個 bit 進行移位與多項式運算, 若最高位為 1 則觸發 XOR 反轉
            if crc & 0x8000:
                crc = (crc << 1) ^ POLYNOMIAL
            else:
                crc = crc << 1
    # 強制截斷保留低 16 位元, 避免 Python 原生大數運算產生越界髒資料
    crc = crc & 0xFFFF  # 確保結果限制在 16-bits 範圍內
    return crc
