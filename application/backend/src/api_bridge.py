# api_bridge.py
"""
[入口] 專門提供給index.py去對接 JS 的 Interface, API 入口類別 (ApiBridge)，串接所有模組

Author: OVT AE
Date: 2026-01-07
Description:
"""
import os
import threading
import time
from datetime import datetime
import gens_mgr
import atbcfg_mgr
import cases_mgr
import cfg_mgr
import report_mgr
import ovvenus
import parse_mgr

class ApiBridge:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self):
        # 初始化中繼介面
        # ----- Frontend
        self.__window = None  # 使用 __ 前綴，防止 pywebview 嘗試將此物件轉成 JS 物件
        # ----- Frontend
        # ----- Service
        self._gens_mgr = gens_mgr.apiGensMgr()
        self._atbcfg_mgr = atbcfg_mgr.apiAtbCfgMgr()
        # ----- Service
        # ----- Board
        self._venus_mgr = None
        self._boardType = 0  # 0: None, 1: MCU, 2: ATB
        # ----- Board
        # ----- Test
        self._cases_mgr = cases_mgr.apiCasesMgr(self)
        self._cfg_mgr = None
        self._report_mgr = report_mgr.apiReportMgr(self)
        self._isTestRunning = False
        self._stopTestProcess = False
        self._startTime = None
        self._Parse_mgr = parse_mgr.apiParseMgr()
        self._txt_out = ""
        self._project_dir = "" # 用來儲存當前載入檔案的根目錄
        # ----- Test

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        ts = "UNKNOWN_TIME"
        try:
            # 如果 datetime 模組在程式關閉時已被銷毀 (None)，這裡會拋出 AttributeError 或 TypeError
            # 如果 datetime 模組還在，這裡就會正常執行
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        except (AttributeError, TypeError, ImportError, NameError):
            # 捕捉所有可能的「模組已銷毀」錯誤
            ts = "SHUTDOWN_TIME"
        except Exception:
            ts = "ERROR_TIME"
        try:
            print(f"[{ts}][{'API_BRIDGE':>16}] {message}", flush=True)
        except ValueError:
            # 防止 stdout 已經被關閉
            pass


    def __scan_worker(self):
        """
        [內部方法] 實際執行硬體掃描的邏輯，跑在 Thread 裡面
        """
        self._log("Scanning thread running...")
        # 1. 重置狀態 (If need)
        # 2. 掃描
        if not self._venus_mgr:
            self._venus_mgr = ovvenus.apiOvVenus()
            self._venus_mgr.venus_device_init()
        # 3. 判斷板子類型
        self._boardType = self._venus_mgr.scan_connected_board()  # 1:MCU 2:ATB
        # 4. 掃描完成，通知前端
        self._log(f"Scan finished. Result boardType={self._boardType}")
        self._trigger_scan_board_result()

    def __test_worker(self, workspace_data):
        """
        [內部方法] 實際執行硬體測試的邏輯，跑在 Thread 裡面
        """
        try:
            self._log("Test thread running...")
            # 重置狀態與檢測
            # --- 檢查必要的管理模組是否存在 ---
            if not self._cases_mgr:
                raise RuntimeError("Cases Manager is None")
            if not self._report_mgr:
                raise RuntimeError("Report Manager is None")
            # 重新掃描硬體
            if not self._venus_mgr:
                self._venus_mgr = ovvenus.apiOvVenus()
                self._venus_mgr.venus_device_init()
            if not self._venus_mgr or not self._venus_mgr._atb_mgr or not self._venus_mgr._mcu_mgr:
                raise RuntimeError("Board Managers are None")
            if not self._cfg_mgr:
                self._cfg_mgr = cfg_mgr.apiCfgMgr(self, self._venus_mgr._atb_mgr)
            self._boardType = self._venus_mgr.scan_connected_board()  # 1:MCU 2:ATB
            board_id = workspace_data.get('gui', {}).get('GLOBAL_BOARD_ID', 0)
            is_simulation = workspace_data.get('gui', {}).get('is_simulation', False)
            # [Simulation] If hardware scan fails (0) but frontend requests simulation
            if is_simulation and self._boardType == 0:
                self._log(f"[Simulation] Simulation Mode detected. Forcing Board Type to {board_id}.")
                self._boardType = board_id
            if self._boardType != board_id:
                msg = "Test Case and Board mismatch! Please correct it"
                if self.__window:
                    self.__window.evaluate_js(f"showToast('{msg}')")
                raise RuntimeError("{msg}")
            # 擷取workspace內容
            ir_data = workspace_data.get('ir_data', {})
            # 更新Test Board Configurations #TOIMPLEMENT
            ret = self._cfg_mgr.configure_board(board_id=board_id, ir_data=ir_data)
            if ret > 1:
                raise RuntimeError("Configure Test Board Failed!")
            # 分析與處理以產生Binary Date #TOIMPLEMENT
            ret = self._cases_mgr.generate_binary_data(ir_data)
            if ret != 0:
                raise RuntimeError("Generate Binary Date Failed!")
            # if simulation, skip below
            if is_simulation:
                self._startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._log("[Simulation] Skipping hardware setup and monitoring.")
                return
            # 將Binary Date下載到Test Board
            ret = self._cases_mgr.download_binary_data()
            if ret != 0:
                raise RuntimeError("Download Binary Date Failed!")
            # 啟動測試
            ret = self.__activate_test()
            if ret != 0:
                raise RuntimeError("Activate Test Failed!")
            self._startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 執行測試步驟...
            while True:
                # 持續週期性檢查Test Board狀態
                time.sleep(1)
                runnin_status = self.is_test_running()
                if not runnin_status:
                    break
                if self._stopTestProcess:
                    abort_test_ret = self._venus_mgr.abort_test()
                    if abort_test_ret != 0:
                        raise RuntimeError("Abort Test Failed!")
                    self._log("Test Aborted!!!")
                    break
            self._log("Test Monitor is finished.")
        except Exception as e:
            # 通知前端測試結束
            self._log(f"Fail: {e}")
        finally:
            # 完成測試: 建立測試報告到應用程式目錄 無論過程中是否發生錯誤
            self._log("Generating report...")
            ret = self._report_mgr.generate_report()
            if ret != 0:
                self._log("Error: Generate Report Failed in cleanup (Code non-zero).")
            # 完成測試: 還原設定與通知前端
            self._isTestRunning = False
            self._stopTestProcess = False
            self._cfg_mgr = None
            # 通知前端測試結束
            self._trigger_test_finish()
            self._log("__test_worker thread is finished.")

    def __activate_test(self):
        """Activate Test Board to start test"""
        if self._venus_mgr:
            return self._venus_mgr.activate_test()
        return -1

    # 通知前端動作區域
    def _trigger_test_finish(self):
        """主動通知前端測試結束"""
        if self.__window:
            # 在 JS 環境執行代碼: 傳入的資料必須轉成 JSON 字串或簡單型別
            self.__window.evaluate_js("window.handleBackendEvent('TEST_FINISHED', null)")

    def _trigger_scan_board_result(self):
        """主動通知前端掃描結束"""
        if self.__window:
            # 在 JS 環境執行代碼: 傳入的資料必須轉成 JSON 字串或簡單型別
            self.__window.evaluate_js(f"window.handleBackendEvent('SCAN_FINISHED', {self._boardType})")

# Interface ---------------------------------------------------------------------------------------------
    def set_window(self, window):
        """JS 端呼叫: api.set_window(window) from index.py"""
        self.__window = window

    def set_app_title(self, file_name, base_title):
        """
        HTML端-JS呼叫: await window.pywebview.api.set_app_title("new_case.json")
        """
        if self.__window:
            new_title = f"{file_name} - {base_title}"
            # 調用 pywebview 視窗物件的 set_title 方法
            self.__window.set_title(new_title)
            # self._log(f"Window title updated to: {new_title}")
        return True

    def scan_board(self):
        """
        HTML端-JS呼叫: await window.pywebview.api.scan_board()
        說明: 啟動一個背景執行緒來執行掃描，避免卡住 UI
        """
        self._log("scan_board called, starting thread...")
        # 建立執行緒，目標指向 self.__scan_worker
        t = threading.Thread(target=self.__scan_worker)
        # 設定為 Daemon thread，這樣當主程式關閉時，這個執行緒也會跟著被強制結束
        t.daemon = True
        t.start()
        # 這裡直接 return (None)，讓 JS 的 await scan_board() 可以先結束，
        # 真正的結果會透過 handleBackendEvent 非同步回傳
        return True

    def open_gens_window(self):
        """
        HTML端-JS呼叫: await window.pywebview.api.open_gens_window()
        """
        # 轉派給實際負責管理視窗的實作層
        if self._gens_mgr:
            return self._gens_mgr.show_gens()
        return None

    def close_gens_window(self):
        """
        JS 端呼叫: await window.pywebview.api.close_gens_window()
        """
        if self._gens_mgr:
            self._log("Closing GENS window...")
            # 請確認您的 gens_mgr 裡面有對應的關閉/隱藏方法
            # 如果是 PyQt/Tkinter，通常是 self.window.close() 或 self.window.hide()
            try:
                self._gens_mgr.close_gens()
            except AttributeError:
                self._log("Warning: gens_mgr has no 'close_gens' method.")
            except Exception as e:
                self._log(f"Error closing gens: {e}")

    def open_atb_config_window(self):
        """
        HTML端-JS呼叫: await window.pywebview.api.open_atb_config_window()
        """
        if self._atbcfg_mgr:
            return self._atbcfg_mgr.show_atbcfg()
        return 0

    def close_atb_config_window(self):
        """
        HTML端-JS呼叫: await window.pywebview.api.close_atb_config_window()
        """
        if self._atbcfg_mgr:
            self._log("Closing ATB CFG window...")
            # 請確認您的 atbcfg_mgr 裡面有對應的關閉/隱藏方法
            # 如果是 PyQt/Tkinter，通常是 self.window.close() 或 self.window.hide()
            try:
                self._atbcfg_mgr.close_atbcfg()
            except AttributeError:
                self._log("Warning: atbcfg_mgr has no 'close_atbcfg' method.")
            except Exception as e:
                self._log(f"Error closing AtbCfg: {e}")

    def start_test_process(self, workspace_data):
        """
        HTML端-JS呼叫: await window.pywebview.api.start_test_process()
        接收來自前端的 Blockly JSON 數據
        workspace_data: dict 型別
        """
        if not self._isTestRunning:
            self._isTestRunning=True
            # 建立執行緒，目標指向 self.__test_worker
            t = threading.Thread(
                target=self.__test_worker,
                args=(workspace_data,)
            )
            # 設定為 Daemon thread，這樣當主程式關閉時，這個執行緒也會跟著被強制結束
            t.daemon = True
            t.start()

    def stop_test_process(self):
        """
        HTML端-JS呼叫: await window.pywebview.api.stop_test_process()
        """
        self._stopTestProcess=True

    def is_test_running(self):
        """
        HTML端-JS呼叫: const isTestRunning = await window.pywebview.api.is_test_running
        回傳: _isTestRunning
        """
        if self._venus_mgr:
            self._isTestRunning = self._venus_mgr.is_test_running()
        else:
            self._isTestRunning = False
        # self._log(f"is_test_running called. Return reseted default: {self._isTestRunning}")
        return self._isTestRunning

    def js_log(self, message):
        """
        接收來自 JS 的 log 並打印在 Python 終端機
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'JS Console':>16}] {message}")

    def Parse_MCU_txt(self, IR_object):
        """
        HTML端-JS呼叫: await window.pywebview.api.set_app_title("new_case.json")
        """
        if self._Parse_mgr:
            self._txt_out = self._Parse_mgr.parse_txt(IR_object, self._project_dir)
        return self._txt_out

    def save_file(self, file_name, content, use_project_dir=True):
        """
        HTML端-JS呼叫: await window.pywebview.api.save_file("test.json", "content", true)
        直接寫入檔案 (不跳出對話框)
        完整路經就會是self._project_dir + file_name
        HTML端-JS呼叫: await window.pywebview.api.save_file("test.json", "content", false)
        跳出對話框選擇檔案位置(包括檔名)並寫入檔案，dialog 預設路徑為 self._project_dir；檔名預設為 file_name
        """
        if use_project_dir:
            # Direct save to project directory
            try:
                file_path = os.path.join(self._project_dir, file_name)
                directory = os.path.dirname(file_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._log(f"File saved directly to: {file_path}")
                return file_path
            except Exception as e:
                self._log(f"Error in save_file (direct): {e}")
                return None
        else:
            # Save with dialog
            if self.__window:
                try:
                    # 直接使用 pywebview 的 window 物件方法
                    # 30 代表 SAVE_DIALOG (避免 import webview 造成循環引用)
                    file_types = ('JSON Files (*.json)', 'Text Files (*.txt)', 'All files (*.*)')
                    result = self.__window.create_file_dialog(
                        30, # SAVE_DIALOG
                        allow_multiple=False,
                        directory=self._project_dir,
                        save_filename=file_name,
                        file_types=file_types
                    )
                    file_path = result[0] if isinstance(result, (list, tuple)) and result else result if isinstance(result, str) else None
                    if file_path:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self._project_dir = os.path.dirname(file_path)
                        self._log(f"File saved via dialog to: {file_path}")
                        return file_path
                except Exception as e:
                    self._log(f"Error in save_file (dialog): {e}")
            return None

    def load_test_case_dialog(self, options=None):
        """
        HTML端-JS呼叫: await window.pywebview.api.load_test_case_dialog(options)
        開啟檔案選擇視窗.
        options (dict):
            - pick_path_only (bool): True 的話只回傳路徑，不讀取內容.
            - file_types (tuple): 檔案類型過濾器.
        """
        if self.__window is None:
            return None
        if options is None:
            options = {}
        pick_path_only = options.get('pick_path_only', False)
        # 新增的行為：只選擇檔案路徑，不開檔
        if pick_path_only:
            if not self._project_dir:
                return {"error": "ERROR_NO_PROJECT_DIR"}
            try:
                file_types = options.get('file_types', ('Text Files (*.txt)', 'All files (*.*)'))
                result = self.__window.create_file_dialog(
                    10, # OPEN_DIALOG
                    allow_multiple=False,
                    directory=self._project_dir,
                    file_types=file_types
                )
                if result and len(result) > 0:
                    file_path = os.path.abspath(result[0])
                    project_dir_abs = os.path.abspath(self._project_dir)
                    try:
                        # 檢查選擇的檔案是否在專案目錄下
                        common = os.path.commonpath([project_dir_abs, file_path])
                        if os.path.normcase(common) == os.path.normcase(project_dir_abs):
                            return {"path": os.path.relpath(file_path, project_dir_abs)}
                        else:
                            return {"error": "ERROR_OUTSIDE_DIR"}
                    except ValueError:
                        # 當路徑在不同磁碟機時會引發 ValueError
                        return {"error": "ERROR_OUTSIDE_DIR"}
            except Exception as e:
                self._log(f"Error in load_test_case_dialog (pick_path_only): {e}")
            return None
        # 原本的行為：開啟專案檔並讀取內容
        else:
            try:
                file_types = options.get('file_types', ('JSON Files (*.json)', 'All files (*.*)'))
                result = self.__window.create_file_dialog(
                    10, # OPEN_DIALOG
                    allow_multiple=False,
                    directory=self._project_dir if self._project_dir else '', # 如果有專案目錄，從那裡開始
                    file_types=file_types
                )
                if result and len(result) > 0:
                    file_path = result[0]
                    if os.path.exists(file_path):
                        # 記錄檔案所在的目錄作為專案根目錄
                        self._project_dir = os.path.dirname(file_path)
                        self._log(f"Project Root set to: {self._project_dir}")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        return { "filename": file_path, "content": content }
                return None
            except Exception as e:
                self._log(f"Error in load_test_case_dialog (load_content): {e}")
                return None

    def get_save_path(self):
        # 1. 檢查 window 是否存在
        if not self.__window:
            return None
        result = self.__window.create_file_dialog(
            10,
            allow_multiple=False,
            file_types=('Text Files (*.txt)', 'All files (*.*)')
        )

        # 3. pywebview 回傳的是一個 Tuple，例如 ('D:/path/to/file.txt',)
        if result and len(result) > 0:
            file_path = result[0]
            return file_path
        return ''

    def script_test_sendfile(self):
        if not self._venus_mgr:
            self._venus_mgr = ovvenus.apiOvVenus()
            self._venus_mgr.venus_device_init()
            self._venus_mgr.set_MCU_connect()

        # 3. 判斷板子類型
        self._boardType = 1  # 1:MCU 2:ATB

        file_path = self.get_save_path()

        # file_path = os.path.join(self._project_dir, '111_parse_mcu.txt')
        if os.path.exists(file_path):
            self._log(f"start script test name {file_path}")
            self._venus_mgr._dev_mgr.send_script_function(file_path)

    def close(self):
        if self._venus_mgr:
            self._venus_mgr.close()
        self._log("Close api_bridge")
