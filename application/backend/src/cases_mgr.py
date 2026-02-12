# cases_mgr.py
"""
[任務] 轉譯 Hex 與下載邏輯

Author: OVT AE
Date: 2026-01-07
Description:
"""
# import json
from datetime import datetime

class apiCasesMgr:
# Internal  ---------------------------------------------------------------------------------------------
    def __init__(self, parent):
        # 初始化中繼管理層
        self.isBusy = False
        self._api_bridge = parent
        self._binary_data = None
        # ----- Blockly
        self.variable_map = {}
        # ----- Blokly
        self._log("apiCasesMgr loaded.")

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'CASEMGR':>16}] {message}")

    # def __process_workspace_json(self, workspace_data):
    #     """
    #     主入口：建立字典並清理數據
    #     """
    #     # 1. 首先提取變數表 (通常在根目錄的 'variables' 鍵下)
    #     self.variable_map = {}
    #     if 'variables' in workspace_data and isinstance(workspace_data['variables'], list):
    #         for var in workspace_data['variables']:
    #             v_id = var.get('id')
    #             v_name = var.get('name')
    #             if v_id and v_name:
    #                 self.variable_map[v_id] = v_name
    #     # 2. 執行遞迴清理
    #     cleaned_data = self.__clean_workspace_data(workspace_data)
    #     return cleaned_data, self.variable_map

    # def __clean_workspace_data(self, data):
    #     """
    #     遞迴清理 Blockly JSON 數據，移除 id, x, y, deletable, languageVersion
    #     """
    #     if isinstance(data, dict):  # 如果是字典，過濾 Key
    #         new_dict = {}
    #         for k, v in data.items():
    #             if k in ['languageVersion', 'collapsed', 'x', 'y', 'deletable', 'movable', 'editable', 'kind']:  # 跳過不需要的 Key
    #                 continue
    #             new_dict[k] = self.__clean_workspace_data(v)  # 遞迴處理數值部分
    #         return new_dict
    #     if isinstance(data, list):  # 如果是列表（例如 blocks 陣列），處理每個元素
    #         return [self.__clean_workspace_data(item) for item in data]
    #     # 基本型別直接回傳
    #     return data

# Interface ---------------------------------------------------------------------------------------------
    def generate_binary_data(self, ir_data=None):
        if not self.isBusy and ir_data:
            self.isBusy = True
            # Debug Area -Start
            # import json
            # self._log("IR Data Content:")
            # self._log(json.dumps(ir_data, indent=2))
            # Debug Area -End
            self._log("generate_binary_data:: Proccess")
            if self._api_bridge._boardType == 1:
                self._binary_data = self._api_bridge.Parse_MCU_txt(ir_data)
                self._log(f"Gen Bin Data: {self._binary_data}")
            self.isBusy = False
            return 0
        return -1

    def download_binary_data(self):
        if self.isBusy:
            self._log("download_binary_data(): is busy")
        self.isBusy = True
        try:
            if not self._api_bridge:
                raise RuntimeError("download_binary_data(): API Bridge is None")
            if not self._api_bridge._venus_mgr:
                raise RuntimeError("download_binary_data(): Venus Manager is None")
            if not self._api_bridge._venus_mgr._dev_mgr:
                raise RuntimeError("download_binary_data(): Device Manager is None")
            if not self._binary_data:
                raise RuntimeError("download_binary_data(): Binary Data is None")
            self._log("download_binary_data:: Proccess")
            ret = self._api_bridge._venus_mgr._dev_mgr.write_testcases(data=self._binary_data)
        except Exception as e:
            self._log(f"download_binary_data(): {e}")
            ret = -1
        finally:
            self._is_busy = False
        return ret
