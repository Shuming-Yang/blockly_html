import sys
import os
import webview  # pip install pywebview

# ---------------------------------------------------------
# 1. PyInstaller 資源路徑處理函數
# ---------------------------------------------------------
def resource_path(relative_path):
    """ 取得資源的絕對路徑，兼容開發環境與 PyInstaller 打包後的環境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包後的臨時目錄
        base_path = sys._MEIPASS
    else:
        # 開發環境下的當前目錄
        base_path = os.path.abspath(".")
    
    # 返回標準化的路徑 (處理 Windows 反斜線問題)
    return os.path.join(base_path, relative_path).replace("\\", "/")

# ---------------------------------------------------------
# 模式 2: Pywebview (推薦)
# ---------------------------------------------------------

# 定義 Python API 供 JS 呼叫
class Api:
    def process_data(self, data):
        print(f"接收到 JS 資料: {data}")
        # 這裡可以做你的邏輯處理
        return f"已收到 '{data}'，處理完成！"

    def start_logic(self):
        print("Python 邏輯啟動")

def open_in_pywebview():
    """
    優點：HTML 可以直接從記憶體載入，不需要寫入實體檔案。
    """
    api = Api()

    #base_uri = pathlib.Path(current_dir).as_uri() + '/'
    #print(base_uri)
    #window = webview.create_window(
    #    'Blockly Tool', 
    #    html=html_content, # 直接傳入字串
    #    url=base_uri,
    #    js_api=api,
    #    width=1200,
    #    height=800
    #)
    window = webview.create_window('Blockly Tool', 'example.html',
        js_api=api,
        width=1200,
        height=800
    )

    webview.start(debug=True) # debug=True 允許按 F12 除錯

# ---------------------------------------------------------
# 主程式入口
# ---------------------------------------------------------
if __name__ == '__main__':
    # 這裡可以做一個簡單的選擇，或直接指定使用哪種方式
    # mode = input("選擇模式 (1: Browser, 2: Pywebview): ")
    # 預設使用 Pywebview
    open_in_pywebview()
