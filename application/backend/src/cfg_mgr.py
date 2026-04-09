# cfg_mgr.py
"""
[任務] 後端配置

Author: OVT AE
Date: 2026-02-24
Description:
採用指令通訊代理模式隔離 GUI 進程,
同時保留原有 Strategy Pattern 結構以便後續開發.
"""
import queue
import tkinter as tk
import multiprocessing
import threading
import time
from typing import Any, Optional, Callable
from shared_utils import global_log

# =============================================================================
# 獨立的 UI 進程函式 (用於隔離 Tkinter 執行緒)
# =============================================================================
def _atb_config_gui_worker(cmd_queue: multiprocessing.Queue) -> None:
    """
    此函式運行在獨立子進程, 負責顯示 UI 並將操作轉發回主進程.
    徹底隔離 Tkinter 的 mainloop 阻塞特性, 避免主測試迴圈遭遇介面卡死.
    """
    try:
        window = tk.Tk()
        window.title("Auto-Test Board Group (ATB)")
        window.geometry("600x550")
        window.resizable(False, False)
        window.attributes('-topmost', True)
        window.columnconfigure(0, weight=1)
        # 確保發送的是一個 Tuple: (str, any), 供主進程的監聽器解析反射呼叫
        def send_cmd(method_name: str, value: Any) -> None:
            try:
                cmd_queue.put((method_name, value))
            except Exception as e:
                global_log(tag="ACGW", message=f"Queue Put Error: {e}")
        # 建立與 UI 雙向綁定的資料變數
        var_sensor_bypass = tk.IntVar(master=window, value=0)
        var_i2c_route = tk.IntVar(master=window, value=1)
        var_mipi_route = tk.IntVar(master=window, value=1)
        var_mclk_source = tk.IntVar(master=window, value=1)
        var_gpio_source = tk.IntVar(master=window, value=1)
        var_fsin_dir = tk.IntVar(master=window, value=1)
        var_strobe_route = tk.IntVar(master=window, value=1)
        var_dovdd = tk.DoubleVar(master=window, value=1.8)
        var_avdd = tk.DoubleVar(master=window, value=2.8)
        var_dvdd = tk.DoubleVar(master=window, value=1.1)
        # 構建 ATB Configurations 介面區塊, 利用括號換行保持單行長度極短
        test_frame = tk.LabelFrame(window, text="ATB Board Configurations", font=("Arial", 12, "bold"), fg="blue", padx=10, pady=10)
        test_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        tk.Label(test_frame, text="Bypass sensor error pin", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Radiobutton(
            test_frame, text="Enable", variable=var_sensor_bypass, value=1,
            command=lambda: send_cmd("set_sensor_error_bypass", var_sensor_bypass.get())
        ).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(
            test_frame, text="Disable", variable=var_sensor_bypass, value=0,
            command=lambda: send_cmd("set_sensor_error_bypass", var_sensor_bypass.get())
        ).grid(row=0, column=2, sticky="w")
        tk.Label(test_frame, text="I2C connect to", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Radiobutton(
            test_frame, text="ATB", variable=var_i2c_route, value=0,
            command=lambda: send_cmd("set_i2c_route", var_i2c_route.get())
        ).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(
            test_frame, text="VENUS", variable=var_i2c_route, value=1,
            command=lambda: send_cmd("set_i2c_route", var_i2c_route.get())
        ).grid(row=1, column=2, sticky="w")
        tk.Label(test_frame, text="MIPI output to", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Radiobutton(
            test_frame, text="ATB", variable=var_mipi_route, value=0,
            command=lambda: send_cmd("set_mipi_route", var_mipi_route.get())
        ).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(
            test_frame, text="VENUS", variable=var_mipi_route, value=1,
            command=lambda: send_cmd("set_mipi_route", var_mipi_route.get())
        ).grid(row=2, column=2, sticky="w")
        tk.Label(test_frame, text="MCLK input from", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        tk.Radiobutton(
            test_frame, text="ATB", variable=var_mclk_source, value=0,
            command=lambda: send_cmd("set_mclk_source", var_mclk_source.get())
        ).grid(row=3, column=1, sticky="w")
        tk.Radiobutton(
            test_frame, text="VENUS", variable=var_mclk_source, value=1,
            command=lambda: send_cmd("set_mclk_source", var_mclk_source.get())
        ).grid(row=3, column=2, sticky="w")
        tk.Label(test_frame, text="GPIO (RST, PWDN, FSIN, STROBE) controlled by", font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        tk.Radiobutton(
            test_frame, text="ATB", variable=var_gpio_source, value=0,
            command=lambda: send_cmd("set_gpio_source", var_gpio_source.get())
        ).grid(row=4, column=1, sticky="w", padx=5)
        tk.Radiobutton(
            test_frame, text="VENUS", variable=var_gpio_source, value=1,
            command=lambda: send_cmd("set_gpio_source", var_gpio_source.get())
        ).grid(row=4, column=2, sticky="w", padx=5)
        tk.Label(test_frame, text="FSIN directory", font=("Arial", 10)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
        tk.Radiobutton(
            test_frame, text="SNR To CAM", variable=var_fsin_dir, value=0,
            command=lambda: send_cmd("set_fsin_dir", var_fsin_dir.get())
        ).grid(row=5, column=1, sticky="w", padx=5)
        tk.Radiobutton(
            test_frame, text="CAM To SNR", variable=var_fsin_dir, value=1,
            command=lambda: send_cmd("set_fsin_dir", var_fsin_dir.get())
        ).grid(row=5, column=2, sticky="w", padx=5)
        tk.Label(test_frame, text="Strobe connect with", font=("Arial", 10)).grid(row=6, column=0, sticky="w", padx=10, pady=5)
        tk.Radiobutton(
            test_frame, text="ATB", variable=var_strobe_route, value=0,
            command=lambda: send_cmd("set_strobe_route", var_strobe_route.get())
        ).grid(row=6, column=1, sticky="w", padx=5)
        tk.Radiobutton(
            test_frame, text="VENUS", variable=var_strobe_route, value=1,
            command=lambda: send_cmd("set_strobe_route", var_strobe_route.get())
        ).grid(row=6, column=2, sticky="w", padx=5)
        # 構建 VDD Group 介面區塊, 利用 Scale 提供精確的電壓調整
        vdd_frame = tk.LabelFrame(window, text="Set VDD Group", font=("Arial", 12, "bold"), fg="blue", padx=10, pady=10)
        vdd_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        tk.Scale(
            vdd_frame, from_=0.8, to=3.9, resolution=0.1, orient=tk.HORIZONTAL,
            label="Sensor DOVDD", variable=var_dovdd, length=400,
            command=lambda v: send_cmd("set_sensor_dovdd", float(v))
        ).grid(row=0, column=0, padx=10)
        tk.Scale(
            vdd_frame, from_=1.3, to=3.2, resolution=0.1, orient=tk.HORIZONTAL,
            label="Sensor AVDD", variable=var_avdd, length=400,
            command=lambda v: send_cmd("set_sensor_avdd", float(v))
        ).grid(row=1, column=0, padx=10)
        tk.Scale(
            vdd_frame, from_=0.8, to=1.5, resolution=0.1, orient=tk.HORIZONTAL,
            label="Sensor DVDD", variable=var_dvdd, length=400,
            command=lambda v: send_cmd("set_sensor_dvdd", float(v))
        ).grid(row=2, column=0, padx=10)
        tk.Button(window, text="Close", width=15, command=window.destroy).grid(row=2, column=0, pady=10)
        # 啟動阻塞式的 UI 事件迴圈, 生命週期與當前子進程綁定
        window.mainloop()
    except Exception as e:
        global_log(tag="CFG_GUI_PROCESS", message=f"Error: {e}")

# =============================================================================
# Strategy Classes (處理邏輯層)
# =============================================================================
class BaseConfigHandler:
    """配置處理器的基底類別, 定義介面合約並提供共用日誌與關閉方法"""
    def __init__(self, parent: Any, ir_data: Optional[Any]) -> None:
        self.parent = parent
        self.ir_data = ir_data
        self._window: Optional[Any] = None

    def _log(self, msg: str) -> None:
        if hasattr(self.parent, '_log'):
            self.parent._log(msg)
        else:
            global_log(tag="Handler", message=msg)

    def run(self, board_id: int) -> int:
        raise NotImplementedError("Subclasses must implement run()")

    def close(self) -> None:
        if hasattr(self.parent, 'close'):
            self.parent.close()

class GuiConfigHandler(BaseConfigHandler):
    """透過代理模式實作 GUI 顯示邏輯, 不直接持有 Tkinter 物件以維持主進程整潔"""
    def run(self, board_id: int) -> int:
        self._log(f"[GUI-Mode] Requesting Proxy GUI for Board: {'ATB' if board_id==2 else 'MCU'}")
        if board_id == apiCfgMgr.BOARD_ID_ATB:
            return self.parent._start_gui_proxy_process()
        return 0

class AutoConfigHandler(BaseConfigHandler):
    """專注於自動化無人值守模式的實作, 保留擴充彈性"""
    def run(self, board_id: int) -> int:
        self._log(f"[Auto-Mode] Processing Board: {'ATB' if board_id==2 else 'MCU'}({board_id})")
        return 0

# =============================================================================
# Manager Class (管理層)
# =============================================================================
class apiCfgMgr:
    API_CFGMGR_AUTOMODE = 0
    API_CFGMGR_GUIMODE = 1
    BOARD_ID_MCU = 1
    BOARD_ID_ATB = 2

    def __init__(self, atb_mgr: Any) -> None:
        self.mode = self.API_CFGMGR_GUIMODE
        self._isBusy = False
        self._atb_mgr = atb_mgr
        self._handler: Optional[BaseConfigHandler] = None
        self._cmd_queue: multiprocessing.Queue = multiprocessing.Queue()
        self._cfg_process: Optional[multiprocessing.Process] = None
        self._stop_listener = threading.Event()
        self._log("apiCfgMgr loaded.")

    def _log(self, message: str) -> None:
        global_log(tag="CFGMGR", message=message)

    def _start_command_listener(self) -> None:
        """啟動獨立執行緒監聽來自 GUI 子進程的佇列指令, 並利用反射機制動態呼叫對應函式"""
        self._stop_listener.clear()
        def listen_loop() -> None:
            self._log("Command Listener Thread Started.")
            while not self._stop_listener.is_set():
                try:
                    # 加入 timeout 確保執行緒可被優雅中斷, 不會永久死鎖
                    item = self._cmd_queue.get(timeout=0.5)
                    if isinstance(item, (tuple, list)) and len(item) == 2:
                        method_name, value = item
                        if hasattr(self, method_name):
                            getattr(self, method_name)(value)
                        elif hasattr(self._atb_mgr, method_name):
                            getattr(self._atb_mgr, method_name)(value)
                        else:
                            self._log(f"Method {method_name} not found in Mgr or ATB_Mgr")
                    else:
                        self._log(f"Received invalid data format from Queue: {item}")
                except queue.Empty:
                    # 精準捕捉佇列超時異常, 若子進程已關閉則主動結束監聽
                    if self._cfg_process and not self._cfg_process.is_alive():
                        break
                    continue
                except Exception as e:
                    self._log(f"Listener error: {e}")
                    break
            self._log("Command Listener Thread Stopped.")
        t = threading.Thread(target=listen_loop, daemon=True)
        t.start()

    def _start_gui_proxy_process(self) -> int:
        """配置並啟動負責渲染 UI 的獨立子進程"""
        self._start_command_listener()
        self._cfg_process = multiprocessing.Process(
            target=_atb_config_gui_worker,
            args=(self._cmd_queue,),
            daemon=True
        )
        self._cfg_process.start()
        return 0

    def _init_board_modules(self, board_id: int) -> int:
        """執行硬體板層級的基礎初始化流程"""
        self._log("Initializing Board Modules...")
        if self._atb_mgr and board_id in [self.BOARD_ID_ATB]:
            ret = self._atb_mgr.init_tcal9539()
            self._atb_mgr.init_atb_oax4kenflag()
            return ret
        return -1

    def configure_board(self, board_id: int = 0, ir_data: Optional[Any] = None, mode: int = 1, wait_for_close: bool = False, check_abort_func: Optional[Callable[[], bool]] = None) -> int:
        """
        執行硬體板的整合配置入口.
        控制阻塞狀態與狀態機, 確保同時間僅有一組配置流程運行.
        """
        if self._isBusy:
            return -1
        self._isBusy = True
        self.mode = mode
        result = -1
        try:
            result = self._init_board_modules(board_id=board_id)
            if result == 0:
                if self.mode == self.API_CFGMGR_GUIMODE:
                    self._handler = GuiConfigHandler(self, ir_data)
                else:
                    self._handler = AutoConfigHandler(self, ir_data)
                # 嚴格篩選僅允許 ATB 板進入 UI 阻擋配置流程
                if board_id in [self.BOARD_ID_ATB]:
                    result = self._handler.run(board_id)
                    if result == 0 and self.mode == self.API_CFGMGR_GUIMODE and wait_for_close:
                        self._log("Waiting for ATB Configuration window to close...")
                        while True:
                            if self._cfg_process and self._cfg_process.is_alive():
                                time.sleep(0.5)
                                # 提供外部中斷機制, 在等待期間依然可接受強制停止指令
                                if check_abort_func and check_abort_func():
                                    self.close()
                                    raise RuntimeWarning("Test aborted during configuration.")
                            else:
                                break
                        self._log("Configuration window closed.")
                else:
                    raise RuntimeError(f"Unknown board_id: {board_id}")
            elif result == 1:
                raise RuntimeError("_init_board_modules() Fail")
        except RuntimeWarning as e:
            # 將外部中斷的異常如實向上拋出, 交由測試迴圈處理收尾
            self._log(f"Warning in configure_board: {e}")
            result = -1
            raise e
        except Exception as e:
            self._log(f"Error: configure_board(): {e}")
            result = -1
        finally:
            self._isBusy = False
        return result

    def close(self) -> None:
        """關閉配置視窗子進程並安全回收監聽器與 IPC 資源"""
        self._stop_listener.set()
        if self._cfg_process and self._cfg_process.is_alive():
            try:
                self._log("Terminating ATB Config process...")
                self._cfg_process.terminate()
                self._cfg_process.join(timeout=1.0)
            except Exception as e:
                self._log(f"Error: terminating ATB process: {e}")
            finally:
                self._cfg_process = None
        self._isBusy = False
        self._log("ATB Config Closed and Resources Cleaned.")
