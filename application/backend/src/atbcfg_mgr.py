# atbCfg.py
import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime

class AtbCfgUI:
# Internal  ---------------------------------------------------------------------------------------------
    def __init__(self, master):
        self.master = master
        self.backcolor = "#f0f0f0" # 承襲原本 globals.backcolor 的概念
        # --- 原本 globals 中的變數，現在變成了 class 內建變數 ---
        self.atb_fw_ver = 0x01020304      # 模擬 globals.atbFwVer
        self.atb_id = "ATB_REV_A"         # 模擬 globals.atbId
        self.atb_status = "Connected"     # 模擬 globals.atbStatus
        # 建立 UI 介面
        self._setup_ui()

    def _setup_ui(self):
        """實作原本 atb_updateGroup() 的內容"""
        container = tk.Frame(self.master, bg=self.backcolor, padx=10, pady=10)
        container.pack(fill=tk.BOTH, expand=True)
        # 1. FPGA / Firmware Group
        atb_group = tk.LabelFrame(container, bg=self.backcolor, text="ATB Board Information", font=("Consolas", 10, "bold"))
        atb_group.pack(fill=tk.X, pady=5)
        t_width = 20
        d_width = 25
        # 顯示版本號 (承襲原本 grid 佈局邏輯)
        tk.Label(atb_group, font=("Consolas", 10), width=t_width, bg=self.backcolor, anchor='w', text='FW Revision:').grid(row=0, column=0, sticky='w')
        tk.Label(atb_group, font=("Consolas", 10), width=d_width, bg=self.backcolor, anchor='w', text=f'0x{self.atb_fw_ver:08X}').grid(row=0, column=1, sticky='w')
        tk.Label(atb_group, font=("Consolas", 10), width=t_width, bg=self.backcolor, anchor='w', text='Board ID:').grid(row=1, column=0, sticky='w')
        tk.Label(atb_group, font=("Consolas", 10), width=d_width, bg=self.backcolor, anchor='w', text=self.atb_id).grid(row=1, column=1, sticky='w')
        # 2. Configuration Group (範例：模擬一些可設定的 Entry)
        cfg_group = tk.LabelFrame(container, bg=self.backcolor, text="ATB Settings", font=("Consolas", 10, "bold"))
        cfg_group.pack(fill=tk.X, pady=5)
        tk.Label(cfg_group, font=("Consolas", 10), width=t_width, bg=self.backcolor, anchor='w', text='Voltage Setting:').grid(row=0, column=0, sticky='w')
        self.volt_entry = tk.Entry(cfg_group, width=15)
        self.volt_entry.insert(0, "3.3")
        self.volt_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        # 3. Apply Button
        btn_apply = tk.Button(container, text="Apply Configuration", command=self.apply_settings, bg="#5cb85c", fg="white")
        btn_apply.pack(pady=10)

# Interface ---------------------------------------------------------------------------------------------
    def apply_settings(self):
        """模擬原本的 apply 邏輯"""
        new_volt = self.volt_entry.get()
        print(f"[ATBCFG] Applied Voltage: {new_volt}")
        messagebox.showinfo("ATB Config", f"Settings applied!\nVoltage: {new_volt}")


class apiAtbCfgMgr:
# Internal  ---------------------------------------------------------------------------------------------
    def __init__(self):
        self._atbCfg_thread = None
        self._lock = threading.Lock()
        # 用來儲存 Tkinter 的 root 物件，以便外部可以控制關閉
        self._root = None

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'ATBCFGMGR':>16}] {message}")

    def _destroy_root(self):
        """實際執行銷毀動作 (由 Tkinter thread 執行)"""
        if self._root:
            try:
                self._root.destroy()
            except Exception as e:
                self._log(f"Error destroying root: {e}")
            finally:
                self._root = None

    def _run_atbcfg_logic(self):
        try:
            self._root = tk.Tk()
            self._root.title("ATB Board Configure Tool")
            self._root.geometry("450x300")
            self._root.resizable(False, False)
            self._root.attributes('-topmost', True)

            def on_close():
                self.close_atbcfg()

            self._root.protocol("WM_DELETE_WINDOW", on_close)
            # --- 在獨立視窗中實例化 AtbCfgUI ---
            # 它會自動把內容塞進這個獨立的 root 視窗
            AtbCfgUI(self._root)
            self._root.mainloop()
        except Exception as e:
            self._log(f"Error starting ATBCFG GUI: {e}")
            self._root = None
        finally:
            self._log("ATBCFG Thread Finished.")

# Interface ---------------------------------------------------------------------------------------------
    def show_atbcfg(self):
        with self._lock:
            # 檢查視窗執行緒是否還在跑
            if self._atbCfg_thread is not None and self._atbCfg_thread.is_alive():
                return "ATBCFG_ALREADY_RUNNING"
            # 建立新執行緒來執行 Tkinter，避免卡住 Blockly
            self._atbCfg_thread = threading.Thread(target=self._run_atbcfg_logic, daemon=True)
            self._atbCfg_thread.start()
            return "ATBCFG_STARTED"

    def close_atbcfg(self):
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
