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
import multiprocessing  # 引入多進程庫以解決 Tkinter 執行緒衝突
from GENS import start_gens
from shared_utils import global_log
try:
    from gens_data import DEFAULT_REGTABLE, DEFAULT_SENSOR_SETTING
except ImportError:
    print("Warning: regtable.py not found! Default files cannot be created.")
    DEFAULT_REGTABLE = ""
    DEFAULT_SENSOR_SETTING = ""

# 獨立的進程啟動函式 (必須放在類別外, 以便 multiprocessing 序列化)
def _run_gens_process_target():
    try:
        root = tk.Tk()
        root.title("GENS Tool")
        root.resizable(False, False)
        root.attributes('-topmost', True)
        # 實體化 Gens 類別
        start_gens(root)
        root.mainloop()
    except Exception as e:
        global_log(tag="RGPT", message=f"Error in GENS Process: {e}")


class apiGensMgr:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self):
        # 將執行緒變更為進程變數
        self._gens_process = None
        self._lock = threading.Lock()

    def _log(self, message):
        global_log(tag="GENSMGR", message=message)

    def _get_default_regtable_content(self):
        return DEFAULT_REGTABLE

    def _get_default_sensor_content(self):
        return DEFAULT_SENSOR_SETTING

    def _check_and_prepare_files(self):
        target_dir = "gens_data"
        files_to_check = {
            "regtable.txt": self._get_default_regtable_content,
            "sensor_setting.txt": self._get_default_sensor_content
        }
        if not os.path.exists(target_dir):
            self._log(f"Directory '{target_dir}' not found. Creating...")
            try:
                os.makedirs(target_dir)
            except OSError as e:
                self._log(f"Error: Failed to create directory {target_dir}: {e}")
                return
        for filename, content_getter in files_to_check.items():
            filepath = os.path.join(target_dir, filename)
            should_create = False
            if not os.path.exists(filepath):
                self._log(f"File '{filename}' missing.")
                should_create = True
            elif os.path.getsize(filepath) == 0:
                self._log(f"File '{filename}' exists but is empty (0 bytes).")
                should_create = True
            if should_create:
                self._log(f"Creating/Overwriting '{filename}' with default content...")
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content_getter())
                except Exception as e:
                    self._log(f"Error: writing file {filename}: {e}")

# Interface ---------------------------------------------------------------------------------------------
    def show_gens(self):
        with self._lock:
            # 檢查進程是否還在跑
            if self._gens_process is not None and self._gens_process.is_alive():
                return "GENS_ALREADY_RUNNING"
            self._check_and_prepare_files()
            # 使用 Process 啟動 GENS, 這會建立一個全新的 Main Thread 環境
            self._gens_process = multiprocessing.Process(
                target=_run_gens_process_target,
                daemon=True
            )
            self._gens_process.start()
            return "GENS_STARTED"

    def close_gens(self):
        """
        提供給外部 (ApiBridge) 呼叫, 用來強制關閉 GENS 視窗
        """
        with self._lock:
            # 關閉獨立進程
            if self._gens_process and self._gens_process.is_alive():
                try:
                    self._log("Attempting to terminate GENS process...")
                    self._gens_process.terminate()  # 強制關閉子進程
                    self._gens_process.join(timeout=1.0)  # 等待資源回收
                    self._gens_process = None
                    self._log("GENS process terminated.")
                    return True
                except Exception as e:
                    self._log(f"Error: terminating process: {e}")
                    return False
            return False
