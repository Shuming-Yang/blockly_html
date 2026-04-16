# cases_mgr.py
"""
[任務] 轉譯 Hex 與下載邏輯

Author: OVT AE
Date: 2026-01-07
Description:
    負責管理測試案例的轉換與下載邏輯.
    整合了 Blockly JSON 轉 Binary 的解析引擎 (原 parse_bin_mgr).
    處理 Hex 檔轉譯, 以及將測試資料透過底層裝置管理器下載至硬體板 (MCU/ATB).
"""
import copy
import os
from typing import Any, Optional
from shared_utils import global_log, crc_16


class apiCasesMgr:
    """
    測試案例管理類別.
    作為前端指令與底層硬體傳輸之間的中介層, 處理測試資料的準備與二進位封包下載排程.
    """
    # 定義感測器設定相關的類別層級常數 (Hex Opcode)
    # 這些常數用於告訴底層韌體該如何解析接下來的資料區塊
    _SNR_CMD_SINGLE = bytes([0xBA])
    _SNR_CMD_BURST = bytes([0xBB])
    _SNR_CMD_DELAY = bytes([0xBC, 0x00])
    _SNR_CMD_HEADER = bytes([0xBF])

# Internal  ---------------------------------------------------------------------------------------------
    def __init__(self, parent: Any) -> None:
        """
        初始化中繼管理層與資料暫存變數.
        使用 Any 標註 parent 以避免與 ApiBridge 產生循環引用 (Circular Import).
        """
        self._api_bridge: Any = parent
        self._datapath: Optional[bytes] = None
        self._settings: Optional[bytes] = None
        self._binary: Optional[bytes] = None
        # Blockly 變數動態對照表
        self._variable_map: dict[str, Any] = {}
        self._log("apiCasesMgr loaded.")

    def _log(self, message: str) -> None:
        """
        轉發內部日誌, 支援極高精度時間戳記 (含微秒) 的偵錯打印.
        """
        global_log(tag="CASEMGR", message=message)

    def _getcmd(self, cmddict: dict[str, Any]) -> bytes:
        """
        解析單一指令字典, 將各個定義好的 Hex 字串欄位轉換為 bytes 格式並緊密拼接.
        設計上支援動態長度的 CmdParams 陣列, 統一轉換後再合併以符合硬體連續記憶體讀取需求.
        """
        # 提取並轉換固定長度欄位, 預設使用 0000 避免解析失敗
        data = bytes.fromhex(cmddict.get('TCId', '0000'))
        data += bytes.fromhex(cmddict.get('CmdType', '0000'))
        data += bytes.fromhex(cmddict.get('GlobalID', '0000'))
        data += bytes.fromhex(cmddict.get('SkipReport', '0000'))
        data += bytes.fromhex(cmddict.get('IfCaseGroup', '0000'))
        data += bytes.fromhex(cmddict.get('ElseCaseGroup', '0000'))
        # 附加動態長度的指令參數, 透過 join 組合空白分隔的 Hex 字串後一次性轉換為二進位流
        data += bytes.fromhex(" ".join(str(num) for num in cmddict.get('CmdParams', [])))
        return data

    def _genbin(self, TestCaseJsonData: dict[str, Any], _project_dir: str = "") -> Optional[bytes]:
        """
        將解析後的前端 JSON 結構徹底轉換為硬體可讀的 test_out.bin 二進位格式.
        包含標頭解析, 建立供硬體快速跳轉的絕對位址偏移表 (Lookup Table), 以及最終 CRC 檢查碼附加.
        """
        self._log('Generate bin from JSON')
        # 建立暫存容器與取得 JSON 中定義的封包總數量 (使用 get 防呆)
        pkg_size: list[int] = []
        pkg_loop_str = TestCaseJsonData.get('header', {}).get('PkgCnt', '0')
        pkg_loop = int(pkg_loop_str, 16)
        # 檢查是否有實質的測試資料需要處理, 避免產出空檔案
        if pkg_loop <= 0:
            self._log("Error: Empty Test Case")
            return None
        write_string = bytes()
        header_pkg_abs = bytes()
        package_list = TestCaseJsonData.get('Package List', [])
        # 遍歷所有封包, 透過安全邊界檢查防止 JSON 標頭宣告數量與實際陣列不符導致越界崩潰
        for i in range(pkg_loop):
            if i >= len(package_list):
                self._log(f"Warning: PkgCnt ({pkg_loop}) exceeds actual package list length.")
                break
            pkg = package_list[i]
            pkg_header_string = bytes.fromhex(pkg.get('nMode', '00'))
            cmddata = pkg.get('Command Lists', [])
            byte_string = bytes()
            # 遍歷封包內的所有指令, 將其轉換為 bytes 並累加
            for j in cmddata:
                byte_string += self._getcmd(copy.deepcopy(j))
            # 紀錄單一封包長度 (4 bytes 本體資訊 + 指令長度), 用於後續記憶體偏移量計算
            pkg_size.append(4 + len(byte_string))
            pkg_header_string += pkg_size[i].to_bytes(2, byteorder='big')
            write_string += pkg_header_string
            write_string += byte_string
        # 若無成功解析出任何封包則提早結束
        if not pkg_size:
            return None
        # 建立硬體跳轉指標表 (Pointer Table): 基礎標頭長度為 (封包數量 * 4 bytes) + 8 bytes 系統前綴
        header_size = (len(pkg_size) * 4) + 8
        header_pkg_abs += header_size.to_bytes(4, byteorder='big')
        # 疊加計算每一個封包在硬體記憶體中的絕對起始位置 (Absolute Offset)
        for i in range(len(pkg_size) - 1):
            header_size += pkg_size[i]
            header_pkg_abs += header_size.to_bytes(4, byteorder='big')
        # 組合最終二進位結構: 封包數 + 總空間大小 + 位址跳轉陣列 + 實際指令資料流
        total_size = header_size + pkg_size[-1]
        bin_string = len(pkg_size).to_bytes(2, byteorder='big')
        bin_string += total_size.to_bytes(4, byteorder='big')
        bin_string += header_pkg_abs
        bin_string += write_string
        # 封裝傳輸層所需的 CRC-16 檢查碼至資料最前端, 供底層韌體驗證資料完整性
        crc_bytes = crc_16(bin_string).to_bytes(2, byteorder='big')
        final_binary_payload = crc_bytes + bin_string
        return final_binary_payload

    def _sl_cmd_set(self, delay_time: str) -> bytes:
        """
        將延遲時間轉譯為硬體專屬的 0xBC 延遲指令二進位資料.
        受限於硬體暫存器配置, 延遲參數最大支援 16-bit 寬度 (即 0xFFFF).
        """
        string = self._SNR_CMD_DELAY
        # 將字串轉換為整數後, 以 Big Endian 轉換為 2 bytes 的硬體通用格式
        string += int(delay_time, 16).to_bytes(2, byteorder='big')
        return string

    def _package_data(self, _dev_id: int, burstwrite: list[int], burst_addr: int) -> bytes:
        """
        根據收集到的暫存器寫入資料長度, 智慧切換 Single Write 或 Burst Write 模式.
        底層暫存器匯流排 (Bus) 處理資料時需要嚴格遵守 4 bytes 對齊 (4-byte alignment) 規範,
        本函式會自動計算餘數並進行補零 (Zero Padding) 以滿足硬體要求.
        """
        bin_string = bytes()
        # 若累積的連續位址資料長度大於 1, 切換至高傳輸效率的 Burst Write 模式
        if len(burstwrite) > 1:
            bin_string = self._SNR_CMD_BURST
            write_len = len(burstwrite)
            bin_string += burst_addr.to_bytes(2, byteorder='big')
            bin_string += write_len.to_bytes(1, byteorder='big')
            bin_string += bytes(burstwrite)
            # 動態補零以滿足硬體層的 4 bytes 記憶體對齊要求, 避免硬體解析錯位
            extend_0 = 4 - (write_len % 4)
            if extend_0 < 4:
                bin_string += bytes(extend_0)
        else:
            # 單一資料直接使用 Single Write 模式, 減少通訊表頭的額外開銷
            bin_string = self._SNR_CMD_SINGLE
            bin_string += burst_addr.to_bytes(2, byteorder='big')
            bin_string += bytes(burstwrite)
        return bin_string

    def _is_hex(self, s: str) -> bool:
        """快速驗證字串是否為純粹的 16 進位字元組成, 作為過濾無效資料的防線"""
        # 移除空白後進行字元比對
        test_str = s.replace(" ", "")
        return all(c in "0123456789ABCDEFabcdef" for c in test_str)

    def _reform(self, file_name: str, project_dir: str = "") -> tuple[bytes, int, int]:
        """
        逐行讀取感測器設定檔 (.txt), 提取 I2C 位址與寫入資料.
        具備連續位址自動聚合機制 (Burst write Aggregation), 大幅減少 I2C 單筆寫入的通訊協定開銷 (Overhead).
        回傳打包好的二進位字串, 位址寬度要求與設備 ID.
        """
        burstwrite: list[int] = []
        burst_addr = 0
        bin_string = bytes()
        offset = 0
        addr_len = 2
        dev_id = 0
        only_allow_dev_id = 0
        # 組合實際的檔案路徑, 並檢查檔案是否存在以防止開檔崩潰
        file_path = os.path.join(project_dir, file_name) if project_dir else file_name
        if not os.path.exists(file_path):
            self._log(f"Warning: Setting file not found -> {file_path}")
            return bin_string, addr_len, dev_id
        # 開啟並逐行讀取檔案內容
        with open(file_path, 'r', encoding='utf-8') as f:
            for commands in f:
                command = commands.split(';')[0].strip()
                if not command:
                    continue
                is_command = command.upper().startswith(('SL', 'DELAY'))
                is_hex_data = self._is_hex(command)
                if is_command:
                    parts = command.split()
                    # 防禦分割後參數不足的問題, 避免 IndexError
                    if len(parts) < 2:
                        continue
                    # 遇到控制指令前, 先將之前快取的資料打包送出以確保執行順序正確
                    if dev_id != 0:
                        bin_string += self._package_data(dev_id, burstwrite, burst_addr)
                    burstwrite.clear()
                    offset = 0
                    bin_string += self._sl_cmd_set(parts[1])
                elif is_hex_data:
                    parts = command.split()
                    # 防禦不完整的 16 進位資料行, 需要包含 dev_id, addr, data 三個要素
                    if len(parts) < 3:
                        continue
                    dev_id, addr, data = map(lambda x: int(x, 16), parts[:3])
                    if only_allow_dev_id == 0:
                        only_allow_dev_id = dev_id
                    # 嚴格限制單一設定檔僅能操作同一顆設備 ID, 且位址不得超越 16-bit 空間
                    if only_allow_dev_id != dev_id or addr > 65535:
                        return bytes(), addr_len, dev_id
                    # 判斷是否需要擴展為 4 bytes 的位址長度標記
                    if addr > 255:
                        addr_len = 4
                    # 判斷當前指令位址是否與上一個連續, 若連續且總量小於硬體緩衝區上限 (64) 則加入 Burst 列隊
                    if addr == (burst_addr + offset) and offset < 64:
                        burstwrite.append(data)
                        offset += 1
                    else:
                        # 記憶體位址不連續或緩衝區已滿, 觸發打包機制
                        if offset != 0:
                            bin_string += self._package_data(dev_id, burstwrite, burst_addr)
                        burstwrite.clear()
                        # 重新設定起始位址並開始新一輪的紀錄
                        burstwrite.append(data)
                        burst_addr = addr
                        offset = 1
        # 檔案讀取結束後, 強制清除並打包仍留在記憶體列隊中的最後一批指令
        if burstwrite:
            bin_string += self._package_data(dev_id, burstwrite, burst_addr)
        # 明確回傳解析出的 dev_id 給外層使用以利標頭封裝
        return bin_string, addr_len, dev_id

    def _header_set(self, setting_no: int, total_len: int, dev_id: int, addr_bit_len: int) -> bytes:
        """
        為單一感測器設定群組建立符合底層通訊協定的專屬標頭.
        包含群組編號, 設備 ID 以及目標記憶體位址寬度標記 (8-bit 暫存器或 16-bit 暫存器).
        """
        header = self._SNR_CMD_HEADER
        header += setting_no.to_bytes(1, byteorder='big')
        header += dev_id.to_bytes(1, byteorder='big')
        # 根據暫存器位址長度寫入硬體識別旗標
        if addr_bit_len == 4:
            header += bytes([0x00])  # 代表 16-bit ADDR
        else:
            header += bytes([0x01])  # 代表 8-bit ADDR
        header += total_len.to_bytes(4, byteorder='big')
        return header

    def _reform_txt_parse(self, group_num: int, filename: str, project_dir: str = "") -> bytes:
        """
        封裝文字設定檔解析, 二進位轉換與系統標頭附加的完整流水線流程.
        """
        # 接收 _reform 回傳的二進位資料, 位址寬度以及設備 ID
        write_str, addr_bit_len, dev_id = self._reform(filename, project_dir)
        # 假如檔案不存在或內部無有效內容, 提早結束避免封裝出無效標頭
        if not write_str:
            return bytes()
        # 計算封包總長度 (純資料長度 + 標頭本身固定的 8 bytes 開銷)
        total_len = len(write_str) + 8
        header_string = self._header_set(group_num, total_len, dev_id, addr_bit_len)
        # 組合標頭與資料回傳
        return header_string + write_str

    def _gen_snrgroup(self, TestCaseJsonData: dict[str, Any], project_dir: str = "") -> Optional[bytes]:
        """
        掃描 JSON 配置中的感測器設定檔列表 (以分號區隔), 逐一解析並串接為連續的二進位映像資料.
        採用 All-or-Nothing 策略: 若遭遇任一檔案解析失敗或遺失, 則整批捨棄以防硬體寫入殘缺資料.
        """
        # 安全地從 JSON 提取檔案清單, 避免層層索引引發 KeyError
        app_area = TestCaseJsonData.get('Application Area', {})
        dev_init = app_area.get('Device Init', {})
        snr_list = dev_init.get('SnrInit', "")
        if not snr_list:
            return None
        # 分割以分號 (;) 分隔的實體檔案清單
        file_list = snr_list.split(';')
        bin_string = bytes()
        # 利用列表推導式依序解析每個檔案並收集結果
        results = [self._reform_txt_parse(n, f, project_dir) for n, f in enumerate(file_list)]
        # 若陣列中有任何一個結果長度為 0 (解析失敗), 則中斷整個群組的生成
        if any(not res for res in results):
            return None
        bin_string += b"".join(results)
        return bin_string

# Interface ---------------------------------------------------------------------------------------------
    def save_binary_files(self, project_dir: str = "") -> None:
        """將記憶體中編譯完成的 Binary 映像與感測器設定落檔至本機儲存空間, 供離線除錯與手動燒錄使用"""
        if self._binary is not None:
            out_path = os.path.join(project_dir, "test_out.bin") if project_dir else "test_out.bin"
            with open(out_path, "wb") as f:
                f.write(self._binary)
        if self._settings is not None:
            out_path = os.path.join(project_dir, "snr_out.bin") if project_dir else "snr_out.bin"
            with open(out_path, "wb") as f:
                f.write(self._settings)

    def generate_binary(self, binary_json: Optional[dict[str, Any]] = None, project_dir: str = "") -> int:
        """
        接收前端組裝的 JSON 測試計畫, 觸發內部編譯引擎生成「測試腳本」與「感測器初始化」的雙路 Binary 映像.
        """
        if binary_json:
            self._log(f"generate_binary:: project_dir:{project_dir}")
            # 呼叫私有方法進行核心測試案例的二進位轉換
            self._binary = self._genbin(TestCaseJsonData=binary_json, _project_dir=project_dir)
            # 呼叫私有方法進行感測器設定檔的聚合轉換 (結果暫存於 self._settings 供下載程序提取)
            self._settings = self._gen_snrgroup(binary_json, project_dir)
            # self.save_binary_files(project_dir)
            if self._settings is not None:
                self._log("No sensor setting file include!")
            if self._binary is not None:
                self._log("Gen Test Bin Success")
                return 0
        return -1

    def download_binary(self, test_mode: int = 0, board_id: int = 2) -> int:
        """
        將編譯妥當的 Binary 映像透過底層 Device Manager 穩態推送至終端硬體 (MCU/ATB).
        具備完善的通訊實例依賴檢查, 防止在未連線或中介層遺失的狀態下觸發硬體異常存取.
        """
        ret = -2  # 預設回傳 -2, 代表模式未支援或尚未執行的狀態
        try:
            # 確保 API 橋接器與底層實體通訊管理員皆已就緒
            if self._api_bridge is None:
                raise RuntimeError("API Bridge is None")
            venus_mgr = self._api_bridge._venus_mgr
            atb_mgr = venus_mgr._atb_mgr
            if atb_mgr is None:
                raise RuntimeError("Device Manager is None")
            # 針對 Binary Test 模式進行下載調度
            if test_mode == 0:
                # 判斷是否為 ATB 載板, 且是否有專屬的資料路徑需要優先配置
                if board_id == 2 and self._datapath is not None:
                    self._log("download datapath")
                # 優先下載通用硬體設定檔 (確保硬體初始化完成)
                if self._settings is not None:
                    self._log("download settings")
                    ret = atb_mgr.write_txtgroup(data=self._settings)
                # 最後將核心測試的 Binary 執行檔寫入硬體記憶體
                if self._binary is not None:
                    self._log("download test binary")
                    ret = atb_mgr.write_testcases(data=self._binary)
            elif test_mode == 1:
                self._log("Not integrated, yet.")
            else:
                raise RuntimeError(f"Test mode {test_mode} is not supported")
        except Exception as e:
            # 捕捉並記錄任何在底層通訊與下載過程中發生的錯誤
            self._log(f"Error: download_binary(): {e}")
            ret = -1
        return ret
