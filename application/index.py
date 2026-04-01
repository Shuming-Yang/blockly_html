# index.py
"""
Device Verification Tool - 應用程式啟動進入點

Author: OVT AE
Date: 2025-12-31
Description:
    此模組為全程式的 Bootloader 負責以下核心任務:
    1. 環境偵測: 判定執行環境 (Dev, PyInstaller OneFile, Nuitka)
    2. 依賴動態注入: 動態修正 sys.path 以載入後端邏輯與原生庫。
    3. 視窗生命週期管理: 初始化 pywebview 並綁定 JS API (ApiBridge)
    4. 日誌雙向導向: 將 Python stdout/stderr 同時輸出至終端機與前端 UI
    5. 效能追蹤: 計算從點擊 EXE 到視窗完全載入的精確啟動時間
    This module serves as the main entry point for the application.
    Environment:
    - Python 3.x
    - Windows + VSCode
    - CMake-driven build for native libraries
"""

# [Pylint 抑制規則]
# C0415: Import outside toplevel (為了動態路徑載入)
# E0401: Unable to import (針對打包後的虛擬路徑)
# W0602/W0603: Global variable usage (用於初始化全域 Bridge 物件)
# pylint: disable=C0415, E0401, W0602, W0603, W0702

import os
import sys
import time
import json
import webview
import psutil

# --- 應用程式中繼資料 ---
APP_VERSION = "0.0.1.6"
APP_TITLE = "Device Verification Tool"

# --- 核心輸出流重組 ---
# 強制設定標準輸出為「行緩衝 (Line Buffering)」，確保 log 訊息不延遲
if sys.stdout:
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')  # type: ignore

if sys.stderr:
    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')  # type: ignore

# 強制 Python 核心不使用緩衝輸出，對子程序 (subprocess) 偵錯尤為重要
os.environ['PYTHONUNBUFFERED'] = '1'

# --- Debug 模式偵測與 Webview 參數注入 ---
is_debug = "--debug" in sys.argv
if is_debug:
    # 開啟遠端偵錯埠 (Edge/Chrome: localhost:9222)
    os.environ['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--remote-debugging-port=9222'
    print("[INDEX] Debug mode enabled")

# 優化 Webview2 效能，禁用不必要的輔助功能與特性
os.environ['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--disable-renderer-accessibility --disable-features=AccessibilityObjectModel'

# 初始化全域變數
ApiBridge = None

class WebviewLogger:
    """
    自定義日誌類別：實現標準輸出重定向。
    將 Python 的 print() 內容同步推送至前端 HTML 介面展示。
    """
    def __init__(self, window):
        self.window = window
        self.terminal = sys.__stdout__ # 備份原始終端機輸出

    def write(self, message):
        if self.terminal:
            self.terminal.write(message)
        msg = message.strip()
        if msg and self.window:
            try:
                # 序列化為 JSON 避免特殊字元（如換行或引號）破壞 JS 字串語法
                msg_json = json.dumps(msg)
                # 呼叫前端全域函式 window.handleBackendEvent
                self.window.evaluate_js(f"window.handleBackendEvent('APP_LOG', {msg_json})")
            except:
                pass

    def flush(self):
        if self.terminal:
            self.terminal.flush()

def get_base_dir():
    """
    動態取得程式執行根路徑：
    1. PyInstaller: 存放在臨時解壓縮目錄 _MEIPASS。
    2. Nuitka/Frozen: 取得執行檔所在的目錄。
    3. Dev: 取得目前 script 所在目錄。
    """
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    if getattr(sys, 'frozen', False) or "nuitka" in sys.modules:
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def initialize_app():
    """
    初始化環境：修正 sys.path 並載入後端核心。
    使用「阻斷式載入」：若核心模組失敗則中止程式，避免不可預期的 Crash。
    """
    global ApiBridge
    base_dir = get_base_dir()
    # 定義需要被納入 Python 搜尋範圍的目錄清單
    paths_to_add = [
        os.path.join(base_dir, 'backend', 'src'),
        os.path.join(base_dir, 'backend', 'src', 'gens'),
        os.path.join(base_dir, 'backend', 'lib'),
    ]
    for p in paths_to_add:
        if os.path.exists(p):
            if p not in sys.path:
                sys.path.insert(0, p)
        else:
            if not getattr(sys, 'frozen', False):
                print(f"[INDEX] Warning: Path not found: {p}")
    try:
        # 動態載入 ApiBridge，此時 sys.path 已經包含 backend/src
        from api_bridge import ApiBridge as BridgeClass
        ApiBridge = BridgeClass
    except ImportError as e:
        print(f"[INDEX] FATAL: Could not load ApiBridge: {e}")
        # GUI 環境下若路徑出錯是致命傷，必須立刻停止以防止靜默失敗
        sys.exit(1)

def get_resource_path(relative_path):
    """取得相對於資源根目錄的絕對路徑 (HTML/CSS/JS)"""
    return os.path.join(get_base_dir(), relative_path)

def run_index():
    """啟動主視窗與 GUI 事件迴圈"""
    global ApiBridge
    html_path = get_resource_path('index.html')
    if ApiBridge is None:
        print("[INDEX] Error: ApiBridge is undefined.")
        return
    # --- 啟動耗時統計邏輯 ---
    startup_timestamp = None
    try:
        current_p = psutil.Process()
        create_time = current_p.create_time()
        startup_timestamp = create_time
        # 針對 PyInstaller OneFile 模式最佳化：
        # OneFile 執行時會先啟動一個 Bootloader (Parent)，再產生子行程運行 Python
        # 抓取 Parent 的啟動時間才是使用者體感上的「真正啟動點」
        if hasattr(sys, '_MEIPASS'):
            parent = current_p.parent()
            if parent and current_p.name() == parent.name():
                parent_create_time = parent.create_time()
                # 若時間差 > 0.5s，判定存在解壓縮過程
                if create_time - parent_create_time > 0.5:
                    print("[INDEX] Detected OneFile Bootloader. Syncing start time.")
                    startup_timestamp = parent_create_time
    except Exception as e:
        print(f"[INDEX] Process metric failed: {e}")
    # 建立視窗與 API 綁定
    api = ApiBridge()
    window = webview.create_window(
        title=f'{APP_TITLE} - v{APP_VERSION}',
        url=html_path,
        js_api=api,
        width=1024,
        height=768,
        resizable=True
    )
    api.set_window(window)
    # 重新定向全域輸出到 Webview 介面
    logger = WebviewLogger(window)
    sys.stdout = logger
    sys.stderr = logger

    def maximize_on_start(window):
        """視窗啟動後的 Callback：處理 UI 最大化與環境參數注入"""
        time.sleep(0.1) # 緩衝以確保 Webview2 渲染引擎已就緒
        window.maximize()
        window.evaluate_js(f"window.APP_TITLE = '{APP_TITLE}'; window.APP_VERSION = '{APP_VERSION}';")
        if startup_timestamp is not None:
            duration = time.time() - startup_timestamp
            print(f"[INDEX] Startup Total Time: {duration:.4f} seconds\n")

    # 進入阻塞式的 GUI 事件迴圈
    webview.start(maximize_on_start, window, debug=is_debug)
    # --- 程式關閉後的清理作業 ---
    print("[INDEX] Window closed. Cleaning up resources...", flush=True)
    if hasattr(api, 'close'):
        api.close()
    print("[INDEX] Application shutdown complete.", flush=True)

if __name__ == '__main__':
    # 針對 Windows 多進程打包的必要修正
    import multiprocessing
    multiprocessing.freeze_support()
    # 強制使用 spawn 模式，與大部分 C-Extension (如 I2C 庫) 較相容
    multiprocessing.set_start_method('spawn', force=True)
    initialize_app()
    try:
        run_index()
    finally:
        pass
