# index.py
"""
Draft Pythin Index

Author: OVT AE
Date: 2025-12-31
Description:
    This module serves as the main entry point for the application.
    Environment:
    - Python 3.x
    - Windows + VSCode
    - CMake-driven build for native libraries
"""
# WARNING
# pylint: disable=C0115, C0116, E0401, W0212
import os
import sys
import time
import webview


def get_resource_path(relative_path):
    """
    取得資源檔案的絕對路徑
    支援開發模式 (一般 python 執行) 與 凍結模式 (PyInstaller 打包後的 exe)
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包後的暫存路徑
        base_path = sys._MEIPASS
    else:
        # 一般開發模式的當前路徑
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# 定義 Python API 供 JS 呼叫
class Api:
    def process_data(self, data):
        print(f"接收到 JS 資料: {data}")
        # 這裡可以做你的邏輯處理
        return f"已收到 '{data}'，處理完成！"

    def start_logic(self):
        print("Python 邏輯啟動")


def run_index():
    # 1. 取得正確的 HTML 路徑
    html_path = get_resource_path(os.path.join('index.html'))
    # 除錯用檢查
    if not os.path.exists(html_path):
        print(f"嚴重錯誤：找不到檔案 {html_path}")
        return
    api = Api()
    # 2. 建立視窗 (先給一個預設大小，稍後會馬上最大化)
    window = webview.create_window(
        title='專案儀表板 (獨立執行版)',
        url=html_path,
        js_api=api,
        width=1024,
        height=768,
        resizable=True
    )

    # 3. 定義啟動時要執行的函式
    def maximize_on_start(window):
        # 等待一小段時間確保視窗已經渲染出來 (可選，但在某些系統上比較保險)
        time.sleep(0.1)
        window.maximize()

    # 4. 啟動並執行最大化
    # 注意：這裡把 window 物件傳進去給 maximize_on_start 用
    # 開發階段先啟用Debug模式
    webview.start(maximize_on_start, window, debug=True)


if __name__ == '__main__':
    run_index()
