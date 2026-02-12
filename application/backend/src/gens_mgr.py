# gens_mgr.py
"""
[任務] GENS Application運作

Author: OVT AE
Date: 2026-01-07
Description:
    管理 GENS Tkinter 視窗的生命週期 (啟動與關閉)
"""
import os
import tkinter as tk
import threading
from datetime import datetime
import GENS
try:
    from gens_data import DEFAULT_REGTABLE, DEFAULT_SENSOR_SETTING
except ImportError:
    # 防止萬一 regtable.py 不見了，程式不會直接崩潰，而是給個空值或報錯
    print("Warning: regtable.py not found! Default files cannot be created.")
    DEFAULT_REGTABLE = ""
    DEFAULT_SENSOR_SETTING = ""

class apiGensMgr:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self):
        self._gens_thread = None
        self._lock = threading.Lock()
        # 用來儲存 Tkinter 的 root 物件，以便外部可以控制關閉
        self._root = None

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'GENSMGR':>16}] {message}")

    def _destroy_root(self):
        """實際執行銷毀動作 (由 Tkinter thread 執行)"""
        if self._root:
            try:
                self._root.destroy()
            except Exception as e:
                self._log(f"Error destroying root: {e}")
            finally:
                self._root = None

    def _run_gens_logic(self):
        try:
            # 1. 在此執行緒中建立 Tkinter Root，並存入 self._root
            self._root = tk.Tk()
            self._root.title("GENS Tool")
            # 禁用視窗調整大小 (Resize)
            self._root.resizable(False, False)
            # 視窗置頂 (Always on Top)
            self._root.attributes('-topmost', True)
            # 設定視窗手動被按 X 關閉時的處理
            def on_close():
                # 呼叫同樣的銷毀邏輯，確保變數被清空
                self._destroy_root()
            self._root.protocol("WM_DELETE_WINDOW", on_close)
            # 實體化 Gens 類別 把剛剛建立的 root 當作 frame 傳進去
            app = GENS.start_gens(self._root)
            # 啟動 Tkinter 事件迴圈
            self._log(f"GUI Loop Started. app::{app}")
            self._root.mainloop()
        except Exception as e:
            self._log(f"Error starting GENS GUI: {e}")
            self._root = None # 確保異常時變數也被清空
        finally:
            self._log("GENS Thread Finished.")

    # 預設 regtable.txt 內容
    def _get_default_regtable_content(self):
        return DEFAULT_REGTABLE

    # 預設 sensor_setting.txt 內容
    def _get_default_sensor_content(self):
        return DEFAULT_SENSOR_SETTING

    # 檢查並建立檔案的核心邏輯
    def _check_and_prepare_files(self):
        target_dir = "gens_data"
        # 定義需要檢查的檔案及其對應的預設內容產生器
        files_to_check = {
            "regtable.txt": self._get_default_regtable_content,
            "sensor_setting.txt": self._get_default_sensor_content
        }
        # 檢查目錄是否存在，不存在則建立
        if not os.path.exists(target_dir):
            self._log(f"Directory '{target_dir}' not found. Creating...")
            try:
                os.makedirs(target_dir)
            except OSError as e:
                self._log(f"Failed to create directory {target_dir}: {e}")
                return  # 無法建立目錄，後續無法進行
        # 檢查檔案是否存在且大小不為 0
        for filename, content_getter in files_to_check.items():
            filepath = os.path.join(target_dir, filename)
            should_create = False
            if not os.path.exists(filepath):
                self._log(f"File '{filename}' missing.")
                should_create = True
            elif os.path.getsize(filepath) == 0:
                self._log(f"File '{filename}' exists but is empty (0 bytes).")
                should_create = True
            # 若需要建立或重建，寫入預設內容
            if should_create:
                self._log(f"Creating/Overwriting '{filename}' with default content...")
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content_getter()) # 呼叫函式取得預設字串
                except Exception as e:
                    self._log(f"Error writing file {filename}: {e}")

# Interface ---------------------------------------------------------------------------------------------
    def show_gens(self):
        with self._lock:
            # 檢查視窗執行緒是否還在跑
            if self._gens_thread is not None and self._gens_thread.is_alive():
                return "GENS_ALREADY_RUNNING"
            self._check_and_prepare_files()
            # 建立新執行緒來執行 Tkinter，避免卡住 Blockly
            self._gens_thread = threading.Thread(target=self._run_gens_logic, daemon=True)
            self._gens_thread.start()
            return "GENS_STARTED"

    def close_gens(self):
        """
        提供給外部 (ApiBridge) 呼叫，用來強制關閉 GENS 視窗
        """
        with self._lock:
            if self._root:
                try:
                    self._log("Attempting to close GENS window...")
                    # 注意：Tkinter 不是 Thread-safe 的，直接呼叫 destroy() 有時會報錯
                    # 使用 after(0, func) 可以將任務排程到 Tkinter 的主執行緒去執行，最安全
                    self._root.after(0, self._destroy_root)
                except Exception as e:
                    self._log(f"Error triggering close: {e}")
