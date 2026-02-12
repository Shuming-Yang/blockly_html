# index.py
"""
Draft Pythin Index

Author: OVT AE
Date: 2025-12-31
Description:
    [啟動點] 建立視窗、綁定 Api 物件
    This module serves as the main entry point for the application.
    Environment:
    - Python 3.x
    - Windows + VSCode
    - CMake-driven build for native libraries
"""
# WARNING
# pylint: disable=C0415, E0401, W0602, W0603, W0702
import os
import sys
import time
import stat
import webview
import psutil

# =================================================================
# ★ 強制設定標準輸出為「行緩衝 (Line Buffering)」
# =================================================================
# 只要遇到換行符號 (\n)，就立刻輸出，不等待緩衝區滿
if sys.stdout:
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')  # type: ignore

if sys.stderr:
    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')  # type: ignore

# 設定環境變數 (給子程序看)
os.environ['PYTHONUNBUFFERED'] = '1'

# 檢查啟動參數中是否有 --debug
is_debug = "--debug" in sys.argv
if is_debug:
    os.environ['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--remote-debugging-port=9222'
    print("[INDEX] Debug mode enabled")

os.environ['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--disable-renderer-accessibility --disable-features=AccessibilityObjectModel'

# 宣告全域變數，確保 run_index 看得到
ApiBridge = None


def get_base_dir():
    """統一取得基礎目錄的邏輯：支援 PyInstaller, Nuitka 與 Dev 環境"""
    # 1. 判定 PyInstaller 打包環境
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    # 2. 判定 Nuitka 或其他編譯環境 (frozen 狀態)
    if getattr(sys, 'frozen', False) or "nuitka" in str(sys.modules):
        # Nuitka onefile 執行時，sys.executable 指向 EXE 真正被執行的位置
        # 或是 Nuitka 虛擬解壓目錄（取決於版本與設定）
        return os.path.dirname(os.path.abspath(sys.executable))
    # 3. 原始 Python 開發環境
    return os.path.dirname(os.path.abspath(__file__))


def initialize_app():
    global ApiBridge
    # 1. 判定路徑：開發環境 vs PyInstaller 環境 or Nuitka 環境
    base_dir = get_base_dir()
    # 2. 強制將 backend/src 加入搜尋路徑
    src_path = os.path.join(base_dir, 'backend', 'src')
    gens_path = os.path.join(src_path, 'gens')
    resource_path = os.path.join(src_path, 'resource')
    lib_path = os.path.join(base_dir, 'backend', 'lib')
    for p in [base_dir, src_path, gens_path, resource_path, lib_path]:
        if os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)
    # 3. 在路徑設定完後才進行 Import
    try:
        import api_bridge
        # 取得類別
        ApiBridge = api_bridge.ApiBridge
    except Exception as e:
        print(f"[INDEX] FATAL: Could not load ApiBridge: {e}")


def get_resource_path(relative_path):
    return os.path.join(get_base_dir(), relative_path)


def run_index():
    # 確保使用全域的 ApiBridge
    global ApiBridge
    html_path = get_resource_path('index.html')
    if ApiBridge is None:
        print("[INDEX] Error: ApiBridge is undefined. The .exe cannot find your backend code.")
        return
    # 取得當前 Process 的建立時間 (使用者點擊 EXE 的時間點)
    startup_timestamp = None
    try:
        current_p = psutil.Process()
        create_time = current_p.create_time()
        # 預設使用當前行程的時間 (適用於 OneDir, 開發環境)
        startup_timestamp = create_time
        # 針對 OneFile 模式的特殊檢查：
        # 如果是 PyInstaller 打包環境 (有 _MEIPASS)
        if hasattr(sys, '_MEIPASS'):
            parent = current_p.parent()
            if parent:
                # 檢查父行程是否還活著，且名字跟我們很像 (或是就是原始的 EXE)
                # 在 Windows OneFile 模式，父行程通常會活著等待子行程結束以清理暫存檔
                try:
                    # 增加名稱比對！
                    # OneFile: Parent(MyApp.exe) -> Child(MyApp.exe)  ==> 名稱相同
                    # OneDir:  Parent(Explorer.exe) -> Child(MyApp.exe) ==> 名稱不同
                    curr_name = current_p.name()
                    parent_name = parent.name()
                    # 只有名稱相同，且時間差合理，才認定是 Bootloader
                    if curr_name == parent_name:
                        parent_create_time = parent.create_time()
                        # 如果兩者出生時間差超過 0.5 秒 (代表有解壓縮過程)
                        if create_time - parent_create_time > 0.5:
                            print("[INDEX] Detected OneFile Bootloader (Parent). Using Parent's start time.")
                            startup_timestamp = parent_create_time
                        else:
                            # 名稱相同但時間差很短，可能是 OneDir 剛好被同名的 script 呼叫，或其他情況
                            # 這種情況通常直接用當前時間即可，或者也可以視為 onefile 啟動很快
                            pass
                    else:
                        # 名稱不同 (例如 Parent 是 explorer.exe)，這絕對是 OneDir 模式
                        print(f"[INDEX] Running in OneDir/Dev mode (Parent is {parent_name}).")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    except Exception as e:
        print(f"[INDEX] Failed to get process info: {e}")
    api = ApiBridge()
    window = webview.create_window(
        title='Device Verification Tool',
        url=html_path,
        js_api=api,
        width=1024,
        height=768,
        resizable=True
    )
    api.set_window(window)

    def maximize_on_start(window):
        time.sleep(0.1)
        window.maximize()
        # 2. 計算並顯示啟動時間
        if startup_timestamp is not None:
            end_time = time.time()
            duration = end_time - startup_timestamp
            msg = f"Startup Total Time: {duration:.4f} seconds"
            # 印在 Console (如果有開 Debug console)
            print(f"[INDEX] {msg}")

    webview.start(maximize_on_start, window, debug=is_debug)  # type: ignore

    # =================================================================
    # 視窗關閉後，程式會執行到這裡！
    # 這時候 Python 環境還很健康，Print 一定看得到
    # =================================================================
    print("[INDEX] Window closed. Cleaning up resources...", flush=True)
    # 呼叫 ApiBridge 的 close 方法
    if hasattr(api, 'close'):
        api.close()
    print("[INDEX] Application shutdown complete.", flush=True)


def remove_readonly(func, path, _):
    """處理 Windows 唯讀檔案或系統鎖定導致刪除失敗的問題"""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


if __name__ == '__main__':
    initialize_app()
    try:
        run_index()
    finally:
        # 在 run_index 結束後呼叫
        pass
