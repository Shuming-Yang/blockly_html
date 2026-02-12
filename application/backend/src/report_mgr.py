# report_mgr.py
"""
[任務] 產生測試報告

Author: OVT AE
Date: 2026-01-07
Description:
"""
import os
import io
import base64
import webbrowser
import ctypes
import time
from datetime import datetime
from typing import Optional
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg') # 強制使用非互動式後端，避免在 Thread 中繪圖噴錯

TEMPLATE_REPORT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Report - {test_board}</title>
    <style>
        body {{
font-family: Arial, sans-serif;
background-color: #f8f9fa;
margin: 40px;
        }}
        h1 {{
border-bottom: 3px solid #007bff;
padding-bottom: 10px;
color: #343a40;
        }}
        .section {{
margin-bottom: 30px;
        }}
        .section h2 {{
color: #007bff;
border-left: 5px solid #007bff;
padding-left: 10px;
        }}
        table {{
width: 100%;
border-collapse: collapse;
margin-top: 10px;
        }}
        th, td {{
border: 1px solid #dee2e6;
padding: 8px;
text-align: left;
        }}
        th {{
background-color: #e9ecef;
        }}
        .pass {{
color: green;
font-weight: bold;
        }}
        .fail {{
color: red;
font-weight: bold;
        }}
    </style>
</head>
<body>

    <details open>
        <summary><h1>Report - {test_board}</h1></summary>

        <details open>
            <summary><h2>Information</h2></summary>
            <div class="section">
                <table>
                    <tr><th>Test Time</th><td>{test_time}</td></tr>
                    <tr><th>Test Flow</th><td>{test_flow}</td></tr>
                </table>
            </div>
        </details>

        <details open>
            <summary><h2>Status</h2></summary>
            <div class="section">
                {test_result_table}
            </div>
        </details>
</body>
</html>
"""

class apiReportMgr:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self, parent):
        # 初始化中繼管理層
        self._DWORD_OF_T_RESULT_HEADER = 6  #Report Header structure size: 6 * u32
        self._DWORD_OF_T_TCOVIEW = 3  # test case overview structure size: 3 * u32
        self._DWORD_OF_T_ERRLOG = 8  # error log structure size: 8 * u32
        self._PRE_IDX_OFFSET = (self._DWORD_OF_T_ERRLOG - 1) * 4  # point to preIdx of structure:t_errlog
        self._TEST_CASE_MAX = 10  # sync to firmware definication
        self._FW_RESULT_ADDRESS = 0
        self._isBusy = False
        self._api_bridge = parent
        self._chip_id = 0
        self._resultSize = 0x2400
        self._resultArray = (ctypes.c_uint8 * self._resultSize)(*([0] * self._resultSize))
        self._resultBurstLength = 48
        self._total_reads = self._resultSize // self._resultBurstLength  # 總共需要讀取的次數
        self._log("apiReportMgr loaded.")

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'REPORT_MGR':>16}] {message}")

    def _generate_formula_image(self, formula: str) -> str:
        """將 LaTeX 數學式轉換為 Base64 編碼的 PNG 圖片"""
        # 建立一個隱藏的圖形
        fig = plt.figure(figsize=(6, 1), dpi=100)
        fig.patch.set_visible(False) # 讓背景透明
        ax = fig.add_subplot(111)
        ax.patch.set_visible(False)
        # 顯示數學式，使用 r'$...$' 格式讓 matplotlib 渲染
        # fontsize 參數可調整大小
        ax.text(0.5, 0.5, r'$' + formula + r'$',
                fontsize=18,
                ha='center',
                va='center')
        ax.axis('off') # 隱藏座標軸
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"

    def _get_report_data(self) -> dict:
        """動態生成並回傳此測試的報告動態內容"""
        # 數學式字串
        # formula = r"Result = \sqrt{\frac{1}{N}\sum_{n = 0}^{N - 1}{(S_{col}\lbrack n\rbrack - S_{avg})}^{2}}"
        # 呼叫函式產生圖片
        # if formula:
        #     formula_image_src = self._generate_formula_image(formula)
        # 報告表格的標題列
        description="Empty"
        results = {}
        test_result="Pass"
        log_table_rows = """
        <tr>
            <th>Log</th>
        </tr>
        """
        log_details_html = "<p>無執行日誌.</p>"
        # 根據 results 建立每一行的資料, 並加入可展開的日誌
        for data in results:
            # 初始化此行的日誌 HTML
            log_details_html = "<p>無執行日誌.</p>"
            if "logs" in data and data["logs"]:
                log_entries = []
                log_entries.append("<pre style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;'>")
                for log_entry in data["logs"]:
                    log_entries.append(f"<code>{log_entry}</code><br>")
                log_entries.append("</pre>")
                log_details_html = "".join(log_entries)
            # `<summary>` 內的連結, 點擊可展開 `<details>` 顯示日誌
            log_table_rows += f"""
        <tr>
            <td>
                <details>
                    <summary style="cursor: pointer; color: blue;">Log Detail</summary>
                    {log_details_html}
                </details>
            </td>
        </tr>
            """
        table_html = f"""
    <div class="section">
        <table>
            <tr><th>Description</th><td>{description}</td></tr>
        </table>
    </div>
    <div class="section">
        <table>
            <tr><th>Item</th><th>Status</th><th>Note</th></tr>
            <tr><td>Check</td><td>{test_result}</td><td>None</td></tr>
        </table>
    </div>
    <details open>
        <summary><h2>Detail</h2></summary>
        <div class="section">
            <table>
                {log_table_rows}
            </table>
        </div>
    </details>
        """
        return {
            "test_result_table": table_html,
            "operator": ["None"],
        }

    def _generate_base64_curve(self, x_data: list[float], y_data: list[float]) -> str:
        fig, ax = plt.subplots()
        ax.plot(x_data, y_data, 'bo--', linewidth=2, markersize=6)
        ax.set_title("Test Curve")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return img_base64

    def _generate_report_html(
        self,
        test_board: str = "",
        start_time: str = "",
        operators: Optional[list[str]] = None,
        test_result_table: str = "",
        open_browser: bool = True
    ):
        """產生報告 HTML 並儲存為 report_<ID>_<timestamp>.html 檔案"""
        try:
            # test_flow 格式轉為 HTML
            test_flow = "<br>".join(operators or [])
            # 取得產出時間與範圍
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not start_time:
                start_time = end_time
            test_time = f"From {start_time} to {end_time}"
            # 替換模板中的佔位符
            filled_html = TEMPLATE_REPORT_HTML.format(
                test_board=test_board,
                test_time=test_time,
                test_flow=test_flow,
                test_result_table=test_result_table,
            )
            x_data: list[float] = []
            y_data: list[float] = []
            # 動態判斷並加入曲線區塊
            if x_data and y_data:
                curve_base64 = self._generate_base64_curve(x_data, y_data)
                curve_image = f"data:image/png;base64,{curve_base64}"
                curve_section = f"""
            <details open>
                <summary><h2>Curve</h2></summary>
                <div class="section" style="text-align: center;">
                    <img src="{curve_image}" alt="Test Curve" style="max-width: 90%; height: auto; display: block; margin: auto;">
                </div>
            </details>
        </details>
    """
                # 將曲線區塊插入到 body 結尾處
                filled_html = filled_html.replace("</body>", f"{curve_section}\n</body>")
            # 儲存檔案
            folder = os.getcwd()
            os.makedirs(folder, exist_ok=True)
            save_start_time = start_time.replace(":", "-").replace(" ", "_")
            filename = f"report_{test_board}_{save_start_time}.html"
            filepath = os.path.join(folder, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(filled_html)
            # 同時更新固定名稱 report.html（會覆蓋）
            fixed_path = os.path.join(folder, "report.html")
            with open(fixed_path, "w", encoding="utf-8") as f:
                f.write(filled_html)
            if open_browser:
                # 自動開啟 HTML 檔案
                self._log("Opening report in browser...")
                webbrowser.open(f"file://{os.path.abspath(fixed_path)}")
            else:
                self._log(f"Report saved to {filepath}, browser skip.")
            return filepath, fixed_path
        except Exception as e:
            self._log(f"Report Generation Failed: {e}")

    def _get_data(self, read_index=0):
        uint32_array = (ctypes.c_uint32 * (self._resultBurstLength + 4))()
        _address = self._FW_RESULT_ADDRESS + (read_index * self._resultBurstLength)  # 計算讀取的地址
        try:
            if self._chip_id == 0x48:  #ATB
                pass
            elif self._chip_id == 0xBC:  #MCU
                pass
            else:
                raise RuntimeError(f"Unknow chip-id:{self._chip_id}")
            return uint32_array
        except Exception as e:
            self._log(f"_get_data Failed: {e}")
            return uint32_array
        finally:
            pass

# Interface ---------------------------------------------------------------------------------------------
    def generate_report(self):
        try:
            if not self._api_bridge or not self._api_bridge._venus_mgr or not self._api_bridge._venus_mgr._dev_mgr:
                raise RuntimeError(f"test board is NULL")
            if not self._isBusy:
                self._isBusy = True
                self._log("generate_report:: Proccess")
                if self._api_bridge._boardType == 1:
                    test_board="MCU"
                    self._chip_id = 0xBC
                    self._FW_RESULT_ADDRESS = 0xC00
                elif self._api_bridge._boardType == 2:
                    test_board="ATB"
                    self._chip_id = 0x48
                    self._FW_RESULT_ADDRESS = 0x4000
                else:
                    test_board="Unknown"
                    raise RuntimeError(f"test_board is {test_board}")
                self._resultArray = self._api_bridge._venus_mgr._dev_mgr.readTestResult()
                # 從測試模組中呼叫方法來取得報告內容
                report_data = self._get_report_data()
                operators = report_data.get("operator", ["None"])
                test_result_table = report_data.get("test_result_table", "")
                self._generate_report_html(test_board=test_board, start_time=self._api_bridge._startTime, operators=operators, test_result_table=test_result_table)
                ret = 0
            else:
                raise RuntimeError("generate_report:: Busy")
        except Exception as e:
            self._log(f"_readTestResult Failed: {e}")
            ret = 0 # here is only for test; it should return -1 when error #TOIMPLEMENT
            # ret = -1
        finally:
            self._isBusy = False
        return ret
