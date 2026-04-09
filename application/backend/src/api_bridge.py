# api_bridge.py
"""
[入口] 專門提供給index.py去對接 JS 的 Interface, API 入口類別 (ApiBridge), 串接所有模組

Author: OVT AE
Date: 2026-01-07
Description:
"""
import os
import threading
import time
import json
from typing import Any, Optional
from datetime import datetime
import serial.tools.list_ports
import serial
from gens_mgr import apiGensMgr
from cases_mgr import apiCasesMgr
from cfg_mgr import apiCfgMgr
from report_mgr import apiReportMgr
from ovvenus import apiOvVenus
from parse_mgr import apiParseMgr
from stream_mgr import apiStreamMgr  # 引入我們寫好的影像串流引擎
from shared_utils import global_log


class ApiBridge:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self) -> None:
        # 初始化中繼介面與前端綁定物件
        self._window: Any = None
        # 建立服務管理員實例，負責控制外部進程與測試邏輯
        self._gens_mgr = apiGensMgr()
        self._cases_mgr = apiCasesMgr(self)
        self._report_mgr = apiReportMgr(self)
        self._parse_mgr = apiParseMgr()
        # 初始化硬體Venus板管理員與設定管理員參考
        self._venus_mgr = apiOvVenus()
        self._cfg_mgr: Optional[apiCfgMgr] = None
        # 初始化測試狀態變數，用於跨執行緒的狀態同步與控制
        self._stop_test_process = False
        self._start_time: Optional[str] = None
        self._test_thread: Optional[threading.Thread] = None
        self._workspace_image_base64: Optional[str] = None
        self._test_mode: int = 0
        self._test_index: int = 0
        self._test_total: int = 0
        self._project_dir: str = "."
        # 初始化 Serial 相關狀態變數與記憶體緩衝區
        self._serial_port: Optional[serial.Serial] = None
        self._serial_thread: Optional[threading.Thread] = None
        self._serial_running = False
        self._serial_logs_buffer: list[str] = []
        self._prev_serial_logs_len = 0
        self._prev_app_logs_len = 0
        self._is_logging_serial = False
        # 初始化 USB 影像串流管理器並綁定回呼函式
        self._stream_mgr = apiStreamMgr()
        self._stream_mgr.set_bridge_callback(self._on_camera_frame)
        self._stream_mgr.set_embl_callback(self._on_embl_data)

    def _log(self, message: str = "") -> None:
        """轉發並印出帶有 API_BRIDGE 標籤的系統日誌"""
        global_log(tag="API_BRIDGE", message=message)

    def _serial_read_worker(self) -> None:
        """背景監聽: 純接收模式 (執行於獨立 Thread)"""
        while self._serial_running and self._serial_port and self._serial_port.is_open:
            try:
                # 若緩衝區無資料, 短暫休眠 1ms 後繼續下一回合, 避免死迴圈佔滿單核心 CPU 資源
                if self._serial_port.in_waiting == 0:
                    time.sleep(0.001)
                    continue
                # 讀取並解碼資料, 使用 ignore 忽略傳輸過程中可能產生的位元錯誤與亂碼
                raw_data = self._serial_port.readline().decode('utf-8', errors='ignore').strip()
                # 確保讀取到有效字串且前端視窗已綁定才進行後續推播
                if not raw_data or not self._window:
                    continue
                # 產生精準到微秒的時間戳記以利後續時序分析
                ts = datetime.now().strftime("%H:%M:%S.%f")
                formatted_data = f"[{ts}] {raw_data}"
                # 紀錄到記憶體緩衝區並設置 50,000 行上限, 防止長時間燒機測試導致記憶體溢位 (OOM)
                if self._is_logging_serial and len(self._serial_logs_buffer) < 50000:
                    self._serial_logs_buffer.append(formatted_data)
                # 將含時間戳的訊息轉為 JSON 格式推播至前端 UI
                msg_json = json.dumps(formatted_data)
                self._window.evaluate_js(f"window.handleBackendEvent('SERIAL_LOG', {msg_json})")
            except Exception as e:
                self._log(f"Serial read worker stopped due to error: {e}")
                # 發生異常 (如 USB 遭意外拔除) 時，確保內部狀態同步關閉
                self._serial_running = False
                break

    def _check_test_managers(self) -> None:
        """確認所有依賴的管理模組已正確實例化，作為測試前的安全防線"""
        if self._cases_mgr is None:
            raise RuntimeError("Cases Manager is None")
        if self._report_mgr is None:
            raise RuntimeError("Report Manager is None")
        if getattr(self._venus_mgr, '_dev_mgr', None) is None:
            raise RuntimeError("Board Managers are None")
        if self._cfg_mgr is None:
            self._cfg_mgr = apiCfgMgr(self._venus_mgr._atb_mgr)

    def _parse_workspace_params(self, workspace_data: dict[str, Any], target_id: int) -> int:
        """從前端傳遞的工作區資料中安全提取專案設定，並進行型別轉換與防呆驗證"""
        if not workspace_data:
            raise RuntimeError("Workspace Data is None or empty")
        # 使用 or {} 防止前端傳遞明確的 null 導致後續 get 報錯
        gui_data = workspace_data.get('gui') or {}
        board_id = gui_data.get('GLOBAL_BOARD_ID', 0)
        # 嚴格驗證觸發的測試按鈕與實際選取的硬體板 ID 是否吻合
        if board_id != target_id:
            raise RuntimeError("Board ID and TEST Board ID not match!")
        # 強制轉型確保後續報告生成模組不會因型別錯誤而崩潰
        self._test_index = int(gui_data.get('testIndex', 0))
        self._test_total = int(gui_data.get('testtotal', 0))
        self._project_dir = str(gui_data.get('projectDir', ""))
        self._workspace_image_base64 = workspace_data.get('workspace_image', None)
        return board_id

    def _execute_and_monitor_binary_test(self) -> None:
        """觸發硬體測試指令，並進入非阻塞式的狀態監控迴圈"""
        if self._venus_mgr.activate_test() != 0:
            raise RuntimeError("Activate Test Failed!")
        self._start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log(f"Test start run {self._start_time}")
        # 持續輪詢硬體狀態，直到測試自然結束或接收到使用者的中斷訊號
        while True:
            time.sleep(1)
            if not self.is_test_running():
                break
            if self._stop_test_process:
                abort_test_ret = self._venus_mgr.abort_test(test_mode=self._test_mode)
                if abort_test_ret != 0:
                    raise RuntimeWarning("Abort Test Failed!")
                self._log("Test Aborted!!!")
                break
        self._log("Test Monitor is finished.")

    def _finalize_test_and_report(self, board_id: int, report_workspace_data: dict[str, Any] | None, worker_name: str, report_only: bool=False) -> None:
        """測試生命週期終點：負責統整數據產出報告，並徹底清理跨執行緒狀態變數"""
        self._log("Generating report...")
        if self._report_mgr and report_workspace_data:
            # 擷取當前所有日誌
            current_serial_logs = list(self._serial_logs_buffer)
            current_app_logs = self._get_app_logs()

            # 僅提取自上次報告以來新增的部分 (解決累積問題)
            new_serial_logs = current_serial_logs[self._prev_serial_logs_len:]
            new_app_logs = current_app_logs[self._prev_app_logs_len:]

            ret = self._report_mgr.generate_report(
                board_id=board_id,
                test_mode=self._test_mode,
                _workspace_data=report_workspace_data,
                _project_dir=self._project_dir,
                _test_index=self._test_index,
                _test_total=self._test_total,
                serial_logs=new_serial_logs,
                _workspace_image_base64=self._workspace_image_base64,
                app_logs_list=new_app_logs
            )
            if ret != 0:
                self._log("Error: Generate Report Failed.")

            # 確保 generate_report() 產生的「系統日誌」不會被算入下一個 Case
            self._prev_serial_logs_len = len(self._serial_logs_buffer)
            self._prev_app_logs_len = len(self._get_app_logs())

        if report_only:
            return
        # 清除硬體通訊標頭紀錄以避免污染下次測試
        if hasattr(self._venus_mgr, '_header_set'):
            setattr(self._venus_mgr, '_header_set', "")
        # 還原所有全域狀態變數，確保下一次測試環境乾淨
        self.stop_serial_logging()
        self._serial_logs_buffer = []
        self._prev_serial_logs_len = 0
        self._prev_app_logs_len = 0
        self._workspace_image_base64 = None
        self._stop_test_process = False
        self._test_thread = None
        self._test_index = 0
        self._test_total = 0
        self._log(f"{worker_name} thread is finished.")
        # 解除前端鎖定狀態
        self._trigger_test_finish()

    def _binary_test_worker(self, workspace_data: Optional[dict[str, Any]] = None, target_id: int = 1) -> None:
        """執行 Binary 燒錄與測試主流程，涵蓋環境驗證、編譯、下載與監控 (執行於獨立 Thread)"""
        board_id = target_id
        safe_workspace = workspace_data if workspace_data is not None else {}
        try:
            self._test_mode = 0
            self._log("Test thread running...")
            self._check_test_managers()
            board_id = self._parse_workspace_params(safe_workspace, target_id)
            self.start_serial_logging()
            # 針對 ATB 載板，需額外喚起設定介面並阻塞等待使用者完成配置
            if board_id == 2 and self._cfg_mgr:
                if self._cfg_mgr.configure_board(board_id, safe_workspace.get('ir_data', {}), self._cfg_mgr.API_CFGMGR_GUIMODE, True, lambda: self._stop_test_process) != 0:
                    raise RuntimeError("Configure Test Board Failed or Aborted!")
                self._log("Configuration window closed, proceeding to generate binary...\n")
            # 呼叫案例管理員將 JSON 參數編譯為可執行的 Binary 格式
            if self._cases_mgr and self._cases_mgr.generate_binary(safe_workspace.get('binary_json', {}), self._project_dir) != 0:
                raise RuntimeError("Generate Binary Date Failed!")
            # 將編譯完成的 Binary 檔案下載至實體硬體板
            if self._cases_mgr and self._cases_mgr.download_binary(self._test_mode, board_id) != 0:
                raise RuntimeError("Download Binary Date Failed!")
            # 準備報告所需的測試內容映射資料
            safe_workspace['test_header'] = ""
            safe_workspace['test_content'] = getattr(self._cases_mgr, '_binary', "")
            # 進入測試狀態輪詢迴圈
            self._execute_and_monitor_binary_test()
        except RuntimeWarning as e:
            self._log(f"Warning: {e}")
        except Exception as e:
            self._log(f"Error: {e}")
        finally:
            # 無論測試成功、失敗或中斷，強制進入收尾與報告生成流程
            self._finalize_test_and_report(board_id, safe_workspace, "_binary_test_worker")

    def _script_test_worker(self, scripts_datas: list[dict[str, Any]]) -> None:
        """執行純文字指令腳本測試主流程，負責逐行下達指令並監控硬體回饋 (執行於獨立 Thread)"""
        script_ws_data_original: dict[str, Any] = {"test_header": "", "test_content": ""}
        try:
            self._test_mode = 1
            self._test_index = 0
            self._test_total = len(scripts_datas)
            header = self._venus_mgr.venus_cfg_titan() # 注入 Titan 硬體專屬的通訊標頭設定
            self._log("Script test thread running...")
            self._start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log(f"Script Test start run {self._start_time}")
            # 寫入預先配置好的硬體初始化標頭設定
            if hasattr(self._venus_mgr, '_header_set') and getattr(self._venus_mgr, '_header_set'):
                script_ws_data_original["test_header"] += "--- [Header Settings] ---\n" + "\n".join(getattr(self._venus_mgr, '_header_set')) + "\n\n"
            # 依序遍歷並傳送所有腳本檔案內容
            for _i, item in enumerate(scripts_datas):
                script_ws_data = script_ws_data_original.copy()
                self._test_index += 1
                self._project_dir = item.get('dir', "")
                self._workspace_image_base64 = item.get('image', None)
                item['content'] = "\n".join(header) + "\n" + item['content']
                content = str(item.get('content', ''))
                # 傳送前檢查是否收到中斷要求
                if self._stop_test_process:
                    self._log("Test Aborted before starting next file!!!")
                    break
                self._log(f"Processing ({self._test_index}/{self._test_total}): {item.get('name')}")
                script_ws_data["test_content"] += f"--- {item.get('name', 'Main Script')} ---\n{content}\n\n"
                if getattr(self._venus_mgr, '_dev_mgr', None):
                    self._venus_mgr._dev_mgr.send_script_content(content)
                self._log("Start to run script")
                # 監控單一腳本執行狀態，直到硬體回報完成 (0x1)
                while True:
                    time.sleep(1)
                    if self._venus_mgr.read_script_status() == 0x1:
                        self._log("Script file finished.")
                        break
                    # 若在執行途中收到中斷要求，主動向硬體發送終止訊號
                    if self._stop_test_process:
                        self._log(f"Test Aborted! abort_test_ret:{self._venus_mgr.abort_test(self._test_mode)}")
                        break
                self._finalize_test_and_report(1, script_ws_data, "_script_test_worker", report_only=True)
                if self._stop_test_process:
                    self._log("Script test process was aborted by user.")
                    break
        except Exception as e:
            self._log(f"Error: Script test worker failed: {e}")
        finally:
            # 強制進入收尾與報告生成流程
            self._finalize_test_and_report(1, None, "_script_test_worker")

    def _monitor_gens_process(self) -> None:
        """背景監控 GENS 外部進程，待其結束後通知前端解鎖 UI"""
        self._log("Start monitoring GENS process...")
        # 只要進程物件存在且還在執行中, 就持續休眠等待
        while self._gens_mgr._gens_process and self._gens_mgr._gens_process.is_alive():
            time.sleep(0.5)
        self._log("GENS process detected as closed. Notifying frontend.")
        # 進程結束或不存在時, 通知前端還原按鈕狀態
        if self._window:
            self._window.evaluate_js("window.handleBackendEvent('GENS_CLOSED', null)")

    def _monitor_atb_config_process(self) -> None:
        """背景監控 ATB 設定視窗進程，待使用者關閉設定後通知前端繼續流程"""
        self._log("Start monitoring ATB Config process...")
        # 只要設定進程存在且還在執行中, 就持續休眠等待
        while self._cfg_mgr and self._cfg_mgr._cfg_process and self._cfg_mgr._cfg_process.is_alive():
            time.sleep(0.5)
        self._log("ATB Config process detected as closed.")
        # 進程結束或不存在時, 通知前端還原按鈕狀態
        if self._window:
            self._window.evaluate_js("window.handleBackendEvent('ATB_CONFIG_CLOSED', null)")

    def _get_app_logs(self) -> list[Any]:
        """透過 JS 注入抓取前端畫面的 APP 日誌，以供寫入最終測試報告"""
        if self._window:
            return self._window.evaluate_js("window.getAppLogsList()")
        return []

    def _trigger_test_finish(self, result_data: Optional[Any] = None) -> None:
        """主動向前端派發測試結束事件，並附帶可選的結果資料載荷"""
        if self._window:
            try:
                if result_data is None:
                    js_code = "window.handleBackendEvent('TEST_FINISHED', null)"
                else:
                    # 確保資料格式安全，防範因不可序列化物件導致崩潰
                    json_str = json.dumps(result_data)
                    js_code = f"window.handleBackendEvent('TEST_FINISHED', {json_str})"
                self._window.evaluate_js(js_code)
            except TypeError:
                self._log("Warning: result_data is not JSON serializable. Sending null.")
                self._window.evaluate_js("window.handleBackendEvent('TEST_FINISHED', null)")

    def _safe_to_int(self, val: Any) -> int:
        """提供高容錯率的整數轉換機制，預設將字串視為 16 進位處理以符合硬體暫存器慣例"""
        try:
            if isinstance(val, int):
                return val
            if isinstance(val, str):
                # 處理空字串的情況
                if not val.strip():
                    return 0
                return int(val, 16)
            return int(val)
        except (ValueError, TypeError):
            # 若轉換失敗, 為了安全起見回傳 0 並記錄警告
            self._log(f"Warning: Failed to convert '{val}' to int, returning 0.")
            return 0

    def _init_venus_safely(self, skip_reinit: bool = False) -> None:
        """提供單一節點的安全硬體連線初始化，阻絕連線異常向外擴散"""
        ret = self._venus_mgr.venus_device_init(skip_reinit)
        if ret != 0:
            raise RuntimeError(f"venus_device_init({skip_reinit}) failed with code {ret}")

    def _on_camera_frame(self, channel: int, base64_data: str, iq_data: Optional[dict] = None) -> None:
        """內部回呼函式：接收來自 stream_mgr 的影像資料或頻寬統計並推送至前端"""
        if self._window:
            try:
                # 處理頻寬統計 (channel == -1 代表頻寬字串)
                if channel == -1:
                    # 直接放入 dumps, 避免 mypy 推斷型別衝突
                    json_str = json.dumps({"value": base64_data})
                    self._window.evaluate_js(f"window.handleBackendEvent('THROUGHPUT', {json_str})")
                    return
                # 影像處理邏輯
                if not base64_data.startswith("data:image"):
                    base64_data = f"data:image/jpeg;base64,{base64_data}"
                # 直接放入 dumps, 字典裡包含 int (channel) 與 str (data)
                payload = {"channel": channel, "data": base64_data}
                if iq_data:
                    payload["iq_data"] = iq_data
                json_str = json.dumps(payload)
                self._window.evaluate_js(f"window.handleBackendEvent('CAMERA_FRAME', {json_str})")
            except Exception as e:
                self._log(f"Error sending frame/throughput to UI: {e}")

    def _on_embl_data(self, _channel: int, hex_list: list[str]) -> None:
        """內部回呼函式：接收來自 stream_mgr 的 EMBL 解析資料並推送至前端"""
        if self._window:
            try:
                json_str = json.dumps(hex_list)
                self._window.evaluate_js(f"window.handleBackendEvent('EMBL_DATA', {json_str})")
            except Exception as e:
                self._log(f"Error sending EMBL to UI: {e}")

# Interface ---------------------------------------------------------------------------------------------
    def set_window(self, window: Any) -> None:
        """供入口程式綁定網頁視窗物件，作為前後端雙向通訊的橋樑"""
        self._window = window

    def set_app_title(self, file_name: str, base_title: str) -> bool:
        """動態更新應用程式視窗標題，顯示當前載入的專案名稱"""
        if self._window:
            new_title = f"{file_name} - {base_title}"
            self._window.set_title(new_title)
        return True

    def open_gens_window(self) -> Optional[str]:
        """啟動 GENS 外部工具並掛載背景監控執行緒"""
        if self._gens_mgr:
            res = self._gens_mgr.show_gens()
            if res == "GENS_STARTED":
                threading.Thread(target=self._monitor_gens_process, daemon=True).start()
            return res
        return None

    def close_gens_window(self) -> None:
        """強制關閉由系統喚起的 GENS 外部工具"""
        if self._gens_mgr:
            self._log("Closing GENS window...")
            try:
                self._gens_mgr.close_gens()
            except AttributeError:
                self._log("Warning: gens_mgr has no 'close_gens' method.")
            except Exception as e:
                self._log(f"Error: closing gens: {e}")

    def open_atb_config_window(self) -> int:
        """初始化硬體並呼叫 ATB 專屬的圖形化設定介面"""
        try:
            # 透過共用方法安全初始化硬體
            self._init_venus_safely(skip_reinit = True)
            # 初始化 ATB 子系統
            if self._venus_mgr._atb_mgr is None:
                self._log("open_atb_config_window(): init _atb_mgr")
                self._venus_mgr.venus_atb_board_init()
            # 確保硬體處於閒置狀態才允許開啟設定介面
            if not self._venus_mgr.is_test_running():
                if self._cfg_mgr is None:
                    self._log("open_atb_config_window(): init _cfg_mgr")
                    self._cfg_mgr = apiCfgMgr(self._venus_mgr._atb_mgr)
                # 啟動設定介面進程
                ret = self._cfg_mgr.configure_board(
                    board_id=self._cfg_mgr.BOARD_ID_ATB,
                    ir_data=None,
                    mode=self._cfg_mgr.API_CFGMGR_GUIMODE
                )
                if ret == 0:
                    threading.Thread(target=self._monitor_atb_config_process, daemon=True).start()
                    return 0
                raise RuntimeError("Configure Test Board Failed")
            raise RuntimeError("The ATB board is running test")
        except Exception as e:
            self._log(f"Error: open_atb_config_window() {e}")
            if self._window:
                self._window.evaluate_js(f"showToast('Error: {str(e)}')")
            return -1

    def close_atb_config_window(self) -> None:
        """主動關閉 ATB 設定介面並釋放相關資源"""
        if self._cfg_mgr:
            self._log("Closing ATB CONFIG window...")
            try:
                self._cfg_mgr.close()
            except AttributeError:
                self._log("Warning: _cfg_mgr has no 'close' method.")
            except Exception as e:
                self._log(f"Error: closing: {e}")
            finally:
                self._cfg_mgr = None

    def check_mcu_status(self) -> int:
        """查詢 MCU 板連線與測試運行狀態"""
        ret = 0
        try:
            # 透過共用方法安全初始化硬體
            self._init_venus_safely(skip_reinit = False)
            # 讀取腳本狀態旗標
            script_sts = self._venus_mgr.read_script_status()
            # 根據硬體暫存器狀態碼判斷目前設備狀態
            if script_sts in (0x0, 0x80):
                # 初始化 MCU 管理物件
                if not self._venus_mgr._mcu_mgr or not self._venus_mgr._dev_mgr:
                    self._venus_mgr.venus_mcu_board_init()
                    self._log("check_mcu_status(): init _mcu_mgr")
                if self._venus_mgr._mcu_mgr.is_device_mcu():
                    if self._venus_mgr.is_test_running():
                        ret = 1
                    self._log("Board detected: MCU")
                else:
                    raise RuntimeError("Not MCU Board")
            elif script_sts == 0x1:
                self._log("check_mcu_status() TEST DONE == IDLE")
            elif script_sts == 0x81:
                self._log("check_mcu_status() TEST RUNNING")
                ret = 1
            else:
                raise RuntimeError("Unhandled Value")
        except Exception as e:
            self._log(f"Error: check_mcu_status(): {e}")
            ret = -1
        return ret

    def check_atb_status(self) -> int:
        """查詢 ATB 板連線、韌體載入與測試運行狀態"""
        ret = 0
        try:
            # 透過共用方法安全初始化硬體
            self._init_venus_safely(skip_reinit = False)
            # 讀取腳本狀態旗標
            script_sts = self._venus_mgr.read_script_status()
            if script_sts in (0x0, 0x80):
                # 初始化 ATB 管理物件
                if not self._venus_mgr._atb_mgr or not self._venus_mgr._dev_mgr:
                    self._venus_mgr.venus_atb_board_init()
                    self._log("check_atb_status(): init _atb_mgr")
                # 切換裝置管理指標並載入韌體
                if self._venus_mgr._atb_mgr.is_device_atb():
                    # 確保裝置通訊通道切換至 ATB 專用介面並載入必要韌體
                    if self._venus_mgr._dev_mgr != self._venus_mgr._atb_mgr:
                        self._venus_mgr._dev_mgr = self._venus_mgr._atb_mgr
                    self._venus_mgr._dev_mgr.loadMainFirmware()
                    if self._venus_mgr.is_test_running():
                        ret = 1
                    else:
                        if self._venus_mgr._atb_mgr._oax4k_only:
                            self._log("check_atb_status(): OAX4k Demo Board")
                        else:
                            self._log("check_atb_status(): ATB")
                    return ret
                raise RuntimeError("Not ATB Board")
            # 防禦硬體錯誤狀態碼交錯問題
            if script_sts == 0x1:
                raise RuntimeError("MCU, but require ATB!")
            if script_sts == 0x81:
                raise RuntimeError("MCU and it is runnning test! ATB is required")
            raise RuntimeError("Unhandled Value")
        except Exception as e:
            self._log(f"Error: check_atb_status(): {e}")
            ret = -1
        return ret

    def start_atb_binary_test(self, workspace_data: dict[str, Any]) -> int:
        """將 ATB Binary 測試任務派發至背景執行緒"""
        if self._test_thread is None:
            self._test_thread = threading.Thread(
                target=self._binary_test_worker,
                args=(workspace_data, 2)
            )
            self._test_thread.daemon = True
            self._test_thread.start()
            return 0
        return 1

    def start_mcu_binary_test(self, workspace_data: dict[str, Any]) -> int:
        """將 MCU Binary 測試任務派發至背景執行緒"""
        if self._test_thread is None:
            self._test_thread = threading.Thread(
                target=self._binary_test_worker,
                args=(workspace_data, 1)
            )
            self._test_thread.daemon = True
            self._test_thread.start()
            return 0
        return 1

    def stop_test_process(self) -> None:
        """設置全域中斷旗標以安全終止測試迴圈"""
        self._stop_test_process = True

    def is_test_running(self) -> bool:
        """提供外部介面快速查詢硬體板當前測試狀態"""
        ret = self._venus_mgr.is_test_running()
        return ret

    def js_log(self, message: str) -> None:
        """接收前端傳遞的 Console 訊息並統合至系統日誌"""
        global_log(tag="JS Console", message=message)

    def Parse_MCU_txt(self, IR_object: dict[str, Any], project_dir: str = "") -> Any:
        """呼叫解析引擎將 IR 結構物件轉譯為目標硬體可讀的測試腳本格式"""
        if self._parse_mgr:
            return self._parse_mgr.parse_txt(IR_object, project_dir)
        return ""

    def save_file_direct(self, file_name: str, file_dir: str, content: str) -> Optional[str]:
        """[API] 靜默儲存：直接將內容寫入指定的目錄與檔案"""
        try:
            full_path = os.path.join(file_dir, file_name)
            directory = os.path.dirname(full_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log(f"File saved directly to: {full_path}")
            return full_path
        except Exception as e:
            self._log(f"Error: in save_file_direct: {e}")
            return None

    def save_file_as_dialog(self, file_name: str, file_dir: str, content: str, file_types: Optional[tuple] = None) -> Optional[str]:
        """[API] 對話框儲存：彈出存檔對話框供使用者選擇完整路徑並儲存"""
        if self._window:
            try:
                # 如果前端沒傳 file_types，則使用通用的預設值 (顯示所有檔案)
                effective_types = file_types if file_types else ('All files (*.*)',)
                result = self._window.create_file_dialog(
                    30, # pywebview.SAVE_DIALOG
                    allow_multiple=False,
                    directory=file_dir,
                    save_filename=file_name,
                    file_types=effective_types
                )
                full_path = result[0] if isinstance(result, (list, tuple)) and result else result if isinstance(result, str) else None
                if full_path:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self._log(f"File saved via dialog to: {full_path}")
                    return full_path
            except Exception as e:
                self._log(f"Error: in save_file_as_dialog: {e}")
        return None

    def _open_file_dialog(self, file_dir: str = "", file_types: Optional[tuple[str, ...]] = None) -> Optional[str]:
        """內部使用的純路徑選取對話框
        :param file_dir: 起始目錄
        :param file_types: 檔案過濾器，例如 ('JSON Files (*.json)', 'All files (*.*)')
        """
        if self._window is None:
            return None
        try:
            # 如果沒傳 type，給予一個寬鬆的預設值
            effective_types = file_types if file_types else ('All files (*.*)',)
            result = self._window.create_file_dialog(
                10, # OPEN_DIALOG
                allow_multiple=False,
                directory=file_dir if file_dir else '',  # 如果有目錄，從那裡開始，否則使用上次紀錄位置
                file_types=effective_types
            )
            if result and len(result) > 0:
                return os.path.abspath(result[0])
        except Exception as e:
            self._log(f"Error: in _open_file_dialog: {e}")
        return None

    def select_file_dialog(self, file_dir: str = "", file_types: Optional[tuple[str, ...]] = None) -> Optional[dict[str, str]]:
        """ 開啟對話框選取檔案路徑 (不讀取內容)
        :param file_dir: 起始目錄
        :param file_types: 檔案過濾器，例如 ('JSON Files (*.json)', 'All files (*.*)')
        """
        abs_path = self._open_file_dialog(file_dir, file_types)
        if abs_path:
            # 直接返回絕對路徑，由前端 (JS) 根據 window.projectDir 自行決定如何處理路徑
            return {"path": abs_path}
        return None

    def load_file_dialog(self, file_dir: str = "", file_types: Optional[tuple[str, ...]] = None) -> Optional[dict[str, Any]]:
        """ 開啟對話框選取並讀取檔案內容 (用於 Load 流程)"""
        abs_path = self._open_file_dialog(file_dir, file_types)
        if abs_path:
            try:
                # 檢查 Magic Number 判斷是否為合法的 OVD 檔案
                is_ovd_file = False
                with open(abs_path, 'rb') as f_bin:
                    # 只讀取檔案開頭的 4 個位元組來做快速Header比對
                    header = f_bin.read(4)
                    if header == b'\x09\x19\xa9\x00':
                        is_ovd_file = True
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return { "filename": abs_path, "content": content, "is_ovd_file": is_ovd_file }
            except Exception as e:
                self._log(f"Error: in load_file_dialog reading: {e}")
        return None

    def script_test_sendfile(self, scripts_datas: Optional[list[dict[str, Any]]] = None) -> int:
        """接收前端傳遞的純文字腳本清單，完成硬體預配置並派發至背景測試執行緒"""
        try:
            if self._test_thread is not None:
                self._log("Warning: Another test is already running.")
                return 1  # Busy
            if not scripts_datas:
                self._log("Error: No script data received.")
                return -1
            # 安全初始化硬體
            self._init_venus_safely(skip_reinit = False)
            # 初始化狀態與綁定資料
            self.start_serial_logging()
            self._venus_mgr.venus_mcu_board_init()
            # 建立並啟動執行緒
            self._test_thread = threading.Thread(target=self._script_test_worker, args=(scripts_datas,))
            self._test_thread.daemon = True
            self._test_thread.start()
            return 0
        except Exception as e:
            self._log(f"Error: Failed to start script test: {e}")
            self.stop_serial_logging()
            # 每次測試完畢後就清空Serial Log Buffer
            self._serial_logs_buffer = []
            # 重新reset venus and FPGA hardware
            self.reset_venus_hardware()
            return -2

    def reset_venus_hardware(self) -> int:
        """送出硬體重置訊號，若正在測試中則拒絕操作"""
        try:
            # 安全初始化硬體
            self._init_venus_safely(skip_reinit = True)
            if self.is_test_running():
                return 1
            self._venus_mgr.reset_venus()
            return 0
        except Exception as e:
            self._log(f"Error: reset_venus_hardware: {e}")
            return -1

    def list_serial_ports(self) -> list[str]:
        """輪詢作業系統並回傳所有可用的 COM Port 實體裝置名稱"""
        try:
            ports = serial.tools.list_ports.comports()
            port_list = [port.device for port in ports]
            return port_list
        except Exception as e:
            self._log(f"Error: listing ports: {e}")
            return []

    def open_serial_port(self, port_name: str, baudrate: int = 115200) -> bool:
        """開啟指定的 COM Port 並獨立啟動資料讀取監聽執行緒"""
        try:
            if self._serial_port and self._serial_port.is_open:
                self.close_serial_port()
            self._serial_port = serial.Serial(port_name, baudrate, timeout=0.1)
            self._serial_running = True
            self._serial_thread = threading.Thread(target=self._serial_read_worker, daemon=True)
            self._serial_thread.start()
            self._log(f"Serial port {port_name} opened.")
            return True
        except Exception as e:
            self._log(f"Error: Failed to open serial port: {e}")
            return False

    def close_serial_port(self) -> bool:
        """關閉 COM Port 連線並通知背景監聽執行緒終止"""
        self._serial_running = False
        if self._serial_port and self._serial_port.is_open:
            self._serial_port.close()
            self._log("Serial port closed.")
        return True

    def start_serial_logging(self) -> bool:
        """開啟開關允許系統將序列埠回傳數據快取至記憶體"""
        if not self._is_logging_serial:
            self._is_logging_serial = True
            self._log("Serial memory logging started.")
        return True

    def stop_serial_logging(self) -> bool:
        """關閉記憶體快取開關並印出本次捕獲的總數據行數"""
        self._is_logging_serial = False
        self._log(f"Serial memory logging stopped. Captured {len(self._serial_logs_buffer)} lines.")
        return True

    def i2c_read(self, id_hex: Any = 0, addr_hex: Any = 0, width_hex: Any = 0) -> dict[str, Any]:
        """執行硬體底層的 I2C 單筆讀取指令，自動處理型別轉換與連線確認"""
        try:
            # 安全初始化硬體
            self._init_venus_safely(skip_reinit = True)
            # 轉換前端傳來的變數
            dev_id = self._safe_to_int(id_hex)
            address = self._safe_to_int(addr_hex)
            width_cfg = self._safe_to_int(width_hex)
            read_val = self._venus_mgr.usbI2cSingleRead(Devid=dev_id, Addr=address, width=width_cfg)
            return {"status": "success", "data": read_val}
        except Exception as e:
            return {"status": "error", "message": f"Error: I2C READ failed: {e}"}

    def i2c_write(self, id_hex: Any, addr_hex: Any, data_hex: Any, width_hex: Any) -> dict[str, Any]:
        """執行硬體底層的 I2C 單筆寫入指令，自動處理型別轉換與連線確認"""
        try:
            # 安全初始化硬體
            self._init_venus_safely(skip_reinit = True)
            # 將字串轉換為整數
            dev_id = self._safe_to_int(id_hex)
            address = self._safe_to_int(addr_hex)
            write_data = self._safe_to_int(data_hex)
            width_cfg = self._safe_to_int(width_hex)
            self._venus_mgr.usbI2cSingleWrite(DevId=dev_id, Addr=address, value=write_data, width=width_cfg)
            return {"status": "success", "message": "Write operation completed."}
        except Exception as e:
            return {"status": "error", "message": f"Error: I2C WRITE failed: {e}"}

    def load_db_file(self, fname=None):
        if fname is None:
            return 0
        self._init_venus_safely(skip_reinit = True)
        return self._venus_mgr.load_db_file(fname=fname)

    def send_db_file(self, setting_index):
        return self._venus_mgr.send_db_file(setting_index=setting_index)

    # =========================================================
    # Camera Stream 預覽相關介面
    # =========================================================
    def start_camera_stream(self, config_json: str) -> int:
        """
        前端請求啟動影像預覽
        :param config_json: 包含影像設定的 JSON 字串
        :return: 0 代表成功啟動，-1 代表失敗
        """
        # self._log(f"Received request to START stream with configs: {config_json}")
        try:
            # 將設定直接交給串流管理員來啟動背景接水執行緒
            is_success = self._stream_mgr.start_stream(config_json)
            if is_success:
                return 0
            return -1
        except Exception as e:
            self._log(f"Error starting stream: {e}")
            return -1

    def stop_camera_stream(self) -> int:
        """
        前端請求停止影像預覽
        """
        self._log("Received request to STOP stream.")
        try:
            # 呼叫串流管理員停止執行緒，並安全釋放 USB 資源
            self._stream_mgr.stop_stream()
            return 0
        except Exception as e:
            self._log(f"Error stopping stream: {e}")
            return -1

    def update_stream_transform(self, mirror: bool, flip: bool) -> None:
        """接收前端傳來的勾選狀態並更新至影像引擎"""
        if self._stream_mgr:
            self._stream_mgr.update_transform(mirror, flip)

    def set_maximized_vc(self, channel: int) -> None:
        """前端通知目前放大的 VC 通道，-1 代表無放大。以此控制背景 IQ 運算以節省 CPU"""
        if self._stream_mgr:
            self._stream_mgr.set_maximized_vc(channel)

    def start_embl(self, vc: int, pos: str, display_length: int) -> int:
        """
        前端請求啟動 EMBL 資料擷取
        純粹的資料切片，無視影像格式 (Format)，只依賴 I2C 給予的絕對長度。
        """
        try:
            # 讀取 I2C 獲取真實長寬 (單位: Bytes)
            read_res = self.i2c_read("64", "70200F00", 0x33)
            reg_val = read_res['data'] if isinstance(read_res, dict) else read_res
            real_w = (reg_val >> 16) & 0xFFFF
            real_h = reg_val & 0xFFFF
            # 兩者相乘直接等於絕對資料長度，不需要管 Format！
            frame_bytes = real_w * real_h
            print(f"[API Bridge] Real Frame Size Acquired -> W:{real_w}, H:{real_h}, TotalBytes:{frame_bytes}")
            if self._stream_mgr:
                is_streaming = self._stream_mgr.capture_thread and self._stream_mgr.capture_thread.is_alive()
                # 檢查串流解析度是否與真實長度同步
                current_cfg = self._stream_mgr.vc_configs.get(vc, {})
                old_w = current_cfg.get('width', 0)
                old_h = current_cfg.get('height', 0)
                needs_restart = is_streaming and (old_w != real_w or old_h != real_h)
                if needs_restart:
                    print("[API Bridge] Resolution mismatch! Restarting USB stream for EMBL...")
                    self._stream_mgr.stop_stream()
                    time.sleep(0.5)
                    is_streaming = False
                # 啟動或重啟串流
                if not is_streaming:
                    print("[API Bridge] Auto-starting USB stream for EMBL...")
                    new_configs = []
                    for ch, cfg in self._stream_mgr.vc_configs.items():
                        if ch == vc:
                            cfg['width'] = real_w
                            cfg['height'] = real_h
                            # EMBL 不管格式，強制設為 5 (RAW8)，讓 USB 底層直接用 W*H*1 去抓資料，保證不會多乘 2 倍！
                            cfg['format'] = 5
                        new_configs.append(cfg)
                    if not new_configs:
                        new_configs.append({
                            "channel": vc,
                            "format": 5, # 同上，純資料模式
                            "width": real_w,
                            "height": real_h,
                            "sequence": "BG"
                        })
                    if not self._stream_mgr.start_stream(json.dumps(new_configs)):
                        return -1
                    time.sleep(0.8)
                # 啟動 EMBL 切片
                return self._stream_mgr.start_embl(vc, pos, frame_bytes, display_length)
            return -1
        except Exception as e:
            print(f"Backend EMBL Start Error: {e}")
            return -1

    def stop_embl(self) -> int:
        """前端請求停止 EMBL 資料擷取"""
        if self._stream_mgr:
            return self._stream_mgr.stop_embl()
        return -1

    def close(self) -> None:
        """應用程式關閉前掛載的清理鉤子，負責釋放核心硬體通訊埠與串流資源"""
        # 確保在程式關閉時，若有影像串流在跑，必須強制停止並釋放 USB
        self.stop_camera_stream()
        self._venus_mgr.close()
        self._log("Close api_bridge")
