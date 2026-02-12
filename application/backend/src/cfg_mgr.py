# cfg_mgr.py
"""
[任務] 後端配置

Author: OVT AE
Date: 2026-01-07
Description: 採用Strategy Pattern的概念來分離 GUI 與 Auto 邏輯 (Design Pattern)
"""
import tkinter as tk
from datetime import datetime


# =============================================================================
# Strategy Classes (處理邏輯層)
# =============================================================================
class BaseConfigHandler:
    """配置處理器的基底類別"""
    def __init__(self, parent, ir_data):
        self.parent = parent      # 指向 apiCfgMgr 或 api_bridge，方便回調
        self.ir_data = ir_data    # 初始化時注入資料
        # 建立變數 (Variable)
        self.var_sensor_bypass = None
        self.var_i2c_route = None
        self.var_mipi_route = None
        self.var_mclk_source = None
        self.var_gpio_source = None
        self.var_fsin_dir = None
        self.var_strobe_route = None
        self.var_dovdd = None
        self.var_avdd = None
        self.var_dvdd = None

    def _log(self, msg):
        """委派回 apiCfgMgr 的 log"""
        if hasattr(self.parent, '_log'):
            self.parent._log(msg)
        else:
            print(f"[Handler] {msg}")

    def run(self, board_id):
        """子類別必須實作此方法"""
        raise NotImplementedError("Subclasses must implement run()")


class GuiConfigHandler(BaseConfigHandler):
    """專注於 GUI 模式的實作"""
    def run(self, board_id):
        self._log(f"[GUI-Mode] Processing Board: {'ATB' if board_id==2 else 'MCU'}({board_id})")
        if board_id == apiCfgMgr.BOARD_ID_ATB:
            # 呼叫 ATB 專用的視窗函式
            self._show_atb_window()
        # 視窗關閉後，程式會繼續執行到這裡
        self._log("[GUI-Mode] ATB Window closed. Returning control to apiCfgMgr.")
        return 0

    def _update_sensor_bypass(self):
        """當 Radiobutton 切換時會呼叫此函式"""
        # 取得當前變數的值
        val = self.var_sensor_bypass.get()
        self._log(f"Bypass sensor ErrPin: {'Enable' if val==1 else 'Disable'} ({val})")
        if self.parent and self.parent._atb_mgr:
            # 呼叫硬體層的函式 set_sensor_error_bypass
            self.parent._atb_mgr.set_sensor_error_bypass(val)
        else:
            self._log("Warning: No hardware manager connected.")

    def _update_i2c_route(self):
        """當 I2C 連線切換時會呼叫此函式"""
        val = self.var_i2c_route.get()
        # 定義: 1=VENUS, 0=ATB
        mode_str = "VENUS" if val == 1 else "ATB"
        self._log(f"I2C connect route changed to: {mode_str} ({val})")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_i2c_route(val)
        else:
            self._log("Warning: No hardware manager connected.")

    def _update_mipi_route(self):
        """MIPI 切換時會呼叫此函式"""
        val = self.var_mipi_route.get()
        # 定義: 1=VENUS, 0=ATB
        mode_str = "VENUS" if val == 1 else "ATB"
        self._log(f"MIPI output route changed to: {mode_str} ({val})")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_mipi_route(val)
        else:
            self._log("Warning: No hardware manager connected.")

    def _update_mclk_source(self):
        """MCLK 來源切換時會呼叫此函式"""
        val = self.var_mclk_source.get()
        # 定義: 1=VENUS, 0=ATB
        mode_str = "VENUS" if val == 1 else "ATB"
        self._log(f"MCLK input source changed to: {mode_str} ({val})")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_mclk_source(val)
        else:
            self._log("Warning: No hardware manager connected.")

    def _update_gpio_source(self):
        """GPIO 來源切換時會呼叫此函式"""
        val = self.var_gpio_source.get()
        # 定義: 1=VENUS, 0=ATB
        mode_str = "VENUS" if val == 1 else "ATB"
        self._log(f"GPIO control source changed to: {mode_str} ({val})")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_gpio_source(val)
        else:
            self._log("Warning: No hardware manager connected.")

    def _update_fsin_dir(self):
        """FSIN 方向切換時會呼叫此函式"""
        val = self.var_fsin_dir.get()
        # 定義: 1=CAM To SNR, 0=SNR To CAM
        mode_str = "CAM To SNR" if val == 1 else "SNR To CAM"
        self._log(f"FSIN directory changed to: {mode_str} ({val})")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_fsin_dir(val)
        else:
            self._log("Warning: No hardware manager connected.")

    def _update_strobe_route(self):
        """Strobe 連線切換時會呼叫此函式"""
        val = self.var_strobe_route.get()
        # 定義: 1=VENUS, 0=ATB
        mode_str = "VENUS" if val == 1 else "ATB"
        self._log(f"Strobe connect with changed to: {mode_str} ({val})")
        if self.parent and self.parent._atb_mgr:
            # 呼叫硬體層 (假設有此函式)
            self.parent._atb_mgr.set_strobe_route(val)
        else:
            self._log("Warning: No hardware manager connected.")

    def _update_dovdd(self, val):
        self._log(f"Set Sensor DOVDD to: {val} V")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_sensor_dovdd(float(val))

    def _update_avdd(self, val):
        self._log(f"Set Sensor AVDD to: {val} V")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_sensor_avdd(float(val))

    def _update_dvdd(self, val):
        self._log(f"Set Sensor DVDD to: {val} V")
        if self.parent and self.parent._atb_mgr:
            self.parent._atb_mgr.set_sensor_dvdd(float(val))

    def _show_atb_window(self):
        """顯示 ATB 配置視窗 (阻塞式)"""
        self._log("Opening ATB Configuration Window...")
        # 建立視窗實體
        window = tk.Tk()
        window.title("Auto-Test Board Group (ATB)")
        window.geometry("600x550")
        # 讓 column 0 (中間那欄) 可以隨著視窗縮放而延展，達到「置中」效果
        window.columnconfigure(0, weight=1)
        # 設定 row 0 (test_frame) 的權重，讓它佔據主要空間 (可選)
        window.rowconfigure(0, weight=1)

        # 定義關閉行為
        def on_close():
            window.destroy()

        # 攔截視窗右上角的 X 按鈕事件
        window.protocol("WM_DELETE_WINDOW", on_close)
        # test-frame標題文字設定在 text 屬性中
        test_frame = tk.LabelFrame(
            window,
            text="ATB Board Configurations",  # Frame 的 Title
            font=("Arial", 12, "bold"),       # 設定 Title 的字體
            fg="blue",                        # 設定 Title 顏色，讓它顯眼一點
            padx=10, pady=10                  # Frame 內部的留白 (Padding)
        )
        # 使用 Grid 布局
        test_frame.grid(
            row=0, column=0,      # 放在第 0 列，第 0 行
            padx=20, pady=20,     # Frame 外部的留白
            sticky="nsew"         # 北南東西 (North-South-East-West) 填滿格子
        )
        # ==================== Row 0: Sensor Bypass ====================
        # 變數預設值處理
        # 使用 IntVar 來儲存選項狀態: 1=Enable, 0=Disable
        self.var_sensor_bypass = tk.IntVar(master=window, value=0)
        # 第一欄: 標籤 (Label)
        lbl_bypass = tk.Label(
            test_frame,
            text="Bypass sensor error pin",
            font=("Arial", 10)
        )
        lbl_bypass.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        # Option 1: Enable (Value=1)
        tk.Radiobutton(
            test_frame,
            text="Enable",
            variable=self.var_sensor_bypass, # 綁定同一個變數
            value=1,                         # 選中時變數值為 1
            command=self._update_sensor_bypass
        ).grid(row=0, column=1, sticky="w", padx=5)
        # Option 2: Disable (Value=0)
        tk.Radiobutton(
            test_frame,
            text="Disable",
            variable=self.var_sensor_bypass, # 綁定同一個變數
            value=0,                         # 選中時變數值為 0
            command=self._update_sensor_bypass
        ).grid(row=0, column=2, sticky="w", padx=5)
        # ==================== Row 1: I2C connect to ====================
        # 初始化變數
        self.var_i2c_route = tk.IntVar(master=window, value=1)
        # Label
        tk.Label(test_frame,
                    text="I2C connect to",
                    font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        # Option 1: ATB (Value=0)
        tk.Radiobutton(test_frame,
                        text="ATB",
                        variable=self.var_i2c_route,
                        value=0,
                        command=self._update_i2c_route).grid(row=1, column=1, sticky="w", padx=5)
        # Option 2: VENUS (Value=1)
        tk.Radiobutton(test_frame,
                        text="VENUS",
                        variable=self.var_i2c_route,
                        value=1,
                        command=self._update_i2c_route).grid(row=1, column=2, sticky="w", padx=5)
        # ==================== Row 2: MIPI output to ====================
        # 初始化變數
        self.var_mipi_route = tk.IntVar(master=window, value=1)
        # Label
        tk.Label(test_frame,
                    text="MIPI output to",
                    font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        # Option 1: ATB (Value=0)
        tk.Radiobutton(test_frame, text="ATB", variable=self.var_mipi_route, value=0,
                        command=self._update_mipi_route).grid(row=2, column=1, sticky="w", padx=5)
        # Option 2: VENUS (Value=1)
        tk.Radiobutton(test_frame, text="VENUS", variable=self.var_mipi_route, value=1,
                        command=self._update_mipi_route).grid(row=2, column=2, sticky="w", padx=5)
        # ==================== Row 3: MCLK input from ====================
        # 初始化變數
        self.var_mclk_source = tk.IntVar(master=window, value=1)
        # Label
        tk.Label(test_frame,
                    text="MCLK input from",
                    font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        # Option 1: ATB (Value=0)
        tk.Radiobutton(test_frame,
                        text="ATB",
                        variable=self.var_mclk_source,
                        value=0,
                        command=self._update_mclk_source).grid(row=3, column=1, sticky="w", padx=5)
        # Option 2: VENUS (Value=1)
        tk.Radiobutton(test_frame,
                        text="VENUS",
                        variable=self.var_mclk_source,
                        value=1,
                        command=self._update_mclk_source).grid(row=3, column=2, sticky="w", padx=5)
        # ==================== Row 4: GPIO controlled by ====================
        # 初始化變數
        self.var_gpio_source = tk.IntVar(master=window, value=1)
        # Label
        tk.Label(test_frame,
                    text="GPIO (RST, PWDN, FSIN, STROBE) controlled by",
                    font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        # Radiobuttons
        tk.Radiobutton(test_frame,
                        text="ATB",
                        variable=self.var_gpio_source,
                        value=0,
                        command=self._update_gpio_source).grid(row=4, column=1, sticky="w", padx=5)
        tk.Radiobutton(test_frame,
                        text="VENUS",
                        variable=self.var_gpio_source,
                        value=1,
                        command=self._update_gpio_source).grid(row=4, column=2, sticky="w", padx=5)
        # ==================== Row 5: FSIN directory ====================
        # 初始化變數 (Default: CAM To SNR = 1)
        self.var_fsin_dir = tk.IntVar(master=window, value=1)
        # Label
        tk.Label(test_frame,
                    text="FSIN directory",
                    font=("Arial", 10)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
        # Option 1: SNR To CAM (Value=0)
        tk.Radiobutton(test_frame,
                        text="SNR To CAM",
                        variable=self.var_fsin_dir,
                        value=0,
                        command=self._update_fsin_dir).grid(row=5, column=1, sticky="w", padx=5)
        # Option 2: CAM To SNR (Value=1)
        tk.Radiobutton(test_frame,
                        text="CAM To SNR",
                        variable=self.var_fsin_dir,
                        value=1,
                        command=self._update_fsin_dir).grid(row=5, column=2, sticky="w", padx=5)
        # ==================== Row 6: Strobe connect with ====================
        # 初始化 (Default: VENUS = 1)
        self.var_strobe_route = tk.IntVar(master=window, value=1)
        # Label
        tk.Label(test_frame,
                    text="Strobe connect with",
                    font=("Arial", 10)).grid(row=6, column=0, sticky="w", padx=10, pady=5)
        # Option 1: ATB (Value=0)
        tk.Radiobutton(test_frame,
                        text="ATB",
                        variable=self.var_strobe_route,
                        value=0,
                        command=self._update_strobe_route).grid(row=6, column=1, sticky="w", padx=5)
        # Option 2: VENUS (Value=1)
        tk.Radiobutton(test_frame,
                        text="VENUS",
                        variable=self.var_strobe_route,
                        value=1,
                        command=self._update_strobe_route).grid(row=6, column=2, sticky="w", padx=5)
        # =====================================================================
        # Frame 2: Set VDD Group (Row 1)
        # =====================================================================
        vdd_frame = tk.LabelFrame(
            window,
            text="Set VDD Group",
            font=("Arial", 12, "bold"),
            fg="blue",
            padx=10,
            pady=10
        )
        vdd_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        vdd_frame.columnconfigure(1, weight=1)
        # 定義初始值
        init_dovdd = 1.8
        init_avdd = 2.8
        init_dvdd = 1.1
        # --- Group 1: DOVDD ---
        self.var_dovdd = tk.DoubleVar(master=window, value=init_dovdd)
        tk.Label(vdd_frame, text="Set Sensor DOVDD: (Set from I2C-Venus)", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        tk.Scale(
            vdd_frame,
            from_=0.8,
            to=3.9,
            resolution=0.1,         # 刻度為 0.1
            orient=tk.HORIZONTAL,   # 橫向
            variable=self.var_dovdd,
            command=self._update_dovdd,
            length=250              # 拉長一點比較好拖曳
        ).grid(row=0, column=1, sticky="w", padx=10)
        # --- Group 2: AVDD ---
        self.var_avdd = tk.DoubleVar(master=window, value=init_avdd)
        tk.Label(vdd_frame, text="Set Sensor AVDD: (Set from I2C-Venus)", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tk.Scale(
            vdd_frame,
            from_=1.3,
            to=3.2,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.var_avdd,
            command=self._update_avdd,
            length=250
        ).grid(row=1, column=1, sticky="w", padx=10)
        # --- Group 3: DVDD ---
        self.var_dvdd = tk.DoubleVar(master=window, value=init_dvdd)
        tk.Label(vdd_frame, text="Set Sensor DVDD: (Set from I2C-Venus)", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        tk.Scale(
            vdd_frame,
            from_=0.8,
            to=1.5,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.var_dvdd,
            command=self._update_dvdd,
            length=250
        ).grid(row=2, column=1, sticky="w", padx=10)
        # 強制執行一次硬體寫入
        self._log("Applying initial VDD values to hardware...")
        self._update_dovdd(init_dovdd)
        self._update_avdd(init_avdd)
        self._update_dvdd(init_dvdd)
        # Close 按鈕
        tk.Button(
            window,
            text="Close",
            width=15,
            height=2,
            command=on_close
        ).grid(row=2, column=0, pady=10, sticky="")
        # 啟動視窗並等待
        window.mainloop()


class AutoConfigHandler(BaseConfigHandler):
    """專注於自動化模式的實作"""
    def run(self, board_id):
        self._log(f"[Auto-Mode] Processing Board: {'ATB' if board_id==2 else 'MCU'}({board_id})")
        # 自動化邏輯直接執行
        return 0


# =============================================================================
# Manager Class (管理層)
# =============================================================================
class apiCfgMgr:
    # Mode Constants
    API_CFGMGR_AUTOMODE = 0
    API_CFGMGR_GUIMODE = 1
    # Board Constants
    BOARD_ID_MCU = 1
    BOARD_ID_ATB = 2

    # Internal ----------------------------------------------------------------
    def __init__(self, parent, atb_mgr):
        self.mode = self.API_CFGMGR_GUIMODE
        self._isBusy = False
        self._api_bridge = parent
        self._atb_mgr = atb_mgr
        self._log("apiCfgMgr loaded.")

    def _log(self, message):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'CFGMGR':>16}] {message}")

    def _init_board_modules(self):
        self._log("Initializing Board Modules...")
        if self._atb_mgr:
            ret = self._atb_mgr.init_tcal9539()
            self._atb_mgr.init_atb_oax4kenflag()
            return ret
        return -1

    # Interface ---------------------------------------------------------------
    def configure_board(self, board_id=0, ir_data=None):
        """
        配置板子的主要入口 - 負責分派任務 (Dispatcher)
        """
        if self._isBusy:
            self._log("configure_board() is busy.")
            return -1
        self._isBusy = True
        result = -1
        try:
            result = self._init_board_modules()
            if result == 0:
                # 根據目前的 mode 決定要實例化哪一個 Handler
                # 將 ir_data 直接傳入 Handler 的初始化中
                if self.mode == self.API_CFGMGR_GUIMODE:
                    handler = GuiConfigHandler(self, ir_data)
                else:
                    handler = AutoConfigHandler(self, ir_data)
                # 執行配置邏輯 apiCfgMgr 不用管細節，只管呼叫 run
                if board_id in [self.BOARD_ID_MCU, self.BOARD_ID_ATB]:
                    result = handler.run(board_id)
                else:
                    self._log(f"Error: Unknown board_id: {board_id}")
                    result = -1
            elif result == 1:
                self._log(f"Run test on ATB: {board_id}")
        except Exception as e:
            self._log(f"Exception during configuration: {e}")
            result = -1
        finally:
            self._isBusy = False
        return result
