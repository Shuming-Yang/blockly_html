# report_mgr.py
"""
[任務] 產生測試報告

Author: OVT AE
Date: 2026-01-07
Description: 
    統一使用 TEMPLATE_REPORT_HTML 進行版面佈局。
    所有的變數透過 _gen_report_html 進行 format 填充。
    支援單次或批次測試完成後，一律統一輸出固定格式的 report_summary.html。
"""
import os
import re
import html
import webbrowser
import ctypes
import json
import time
from pathlib import Path
import threading
from datetime import datetime
from typing import Optional, Any
from shared_utils import global_log

# ============================================================================
# 共用 CSS 樣式 (獨立出來，讓個別報告與合併報告都能套用)
# ============================================================================
COMMON_CSS = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #eef2f5;
            margin: 40px auto;
            max-width: 1200px;
            color: #333;
        }
        
        .report-container {
            background-color: #f4f6f9;
            border: 1px solid #ccc;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .report-header {
            background-color: #005f9e;
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            font-size: 1.6em;
            font-weight: bold;
            list-style: none;
            display: flex;
            align-items: center;
            transition: background-color 0.3s;
            outline: none;
        }
        .report-header:hover { background-color: #004a7c; }
        .report-header::-webkit-details-marker { display: none; }
        .report-header::before {
            content: '▶';
            display: inline-block;
            width: 30px;
            font-size: 0.8em;
            transition: transform 0.3s ease;
        }
        details[open] > .report-header::before { transform: rotate(90deg); }
        
        .report-body { padding: 20px; }
        h2 { color: #007acc; border-left: 5px solid #007acc; padding-left: 10px; margin-top: 10px; }
        h3 { color: #444; margin-top: 25px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
        .section { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #dee2e6; padding: 10px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: 600; width: 20%; }
        .pass { color: #28a745; font-weight: bold; }
        .fail { color: #dc3545; font-weight: bold; }
        .empty-text { color: #888; font-style: italic; }
        
        .result-line { padding: 8px; border-bottom: 1px solid #eee; font-family: 'Consolas', monospace; font-size: 14px; }
        .result-line:last-child { border-bottom: none; }
        .result-line:nth-child(even) { background-color: #fcfcfc; }

        .terminal-log {
            background-color: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 6px; max-height: 400px;
            overflow-y: auto; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px;
            line-height: 1.5; white-space: pre-wrap; word-wrap: break-word;
        }
        
        .sequence-container { width: 100%; overflow-x: auto; overflow-y: hidden; text-align: center; padding: 10px 0; }
        .sequence-img { max-width: none; height: auto; min-width: 100%; }
        details > summary { outline: none; }
        
        .main-summary {
            cursor: pointer; font-weight: bold; color: #1e1e1e; background-color: #e9ecef;
            padding: 12px 15px; border-radius: 6px; border-left: 5px solid #007acc; margin-top: 20px;
            margin-bottom: 10px; font-size: 1.3em; transition: background-color 0.2s;
        }
        .main-summary:hover { background-color: #dde2e6; }
        
        .test-content-wrapper {
            border: 1px solid #dee2e6; background-color: #fafbfc; padding: 5px 25px 25px 25px;
            border-radius: 0 0 8px 8px; border-top: none; margin-top: -10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.03);
        }
"""

# ============================================================================
# 單一報告 HTML 模板
# ============================================================================
TEMPLATE_REPORT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {test_board}</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <details class="report-container" open>
        <summary class="report-header">
            Device Verification Report - {test_board} ({MODE} Mode) - Test Index:{test_index}
        </summary>
        <div class="report-body">
            <h2>General Information</h2>
            <div class="section">
                <table>
                    <tr><th>Target Board</th><td>{test_board}</td></tr>
                    <tr><th>Test Index</th><td>{test_index} / {test_total}</td></tr>
                    <tr><th>Test Mode</th><td>{MODE}</td></tr>
                    <tr><th>Test Folder</th><td>{folder}</td></tr>
                    <tr><th>Test Period</th><td>{test_time}</td></tr>
                    <tr><th>Overall Status</th><td>{overall_status}</td></tr>
                </table>
            </div>
            <details close>
                <summary class="main-summary">Detailed Test Content (Click to Collapse/Expand)</summary>
                <div class="test-content-wrapper">
                    <h3>Test Results</h3>
                    <div class="section" style="padding: 10px 20px;">
                        {test_result_content}
                    </div>
                    <h3>Hardware Serial Logs</h3>
                    <div class="section">
                        <div class="terminal-log">{serial_logs}</div>
                    </div>
                    <h3>Application System Logs</h3>
                    <div class="section">
                        <div class="terminal-log">{app_logs}</div>
                    </div>
                    {test_header_section}
                    {test_content_section}
                    {sequence_diagram_section}
                </div>
            </details>
        </div>
    </details>
</body>
</html>
"""

class apiReportMgr:
# Internal ---------------------------------------------------------------------------------------------
    def __init__(self, parent: Any) -> None:
        """初始化報告管理員, 定義硬體記憶體對齊常數與暫存緩衝區"""
        self._DWORD_OF_T_RESULT_HEADER = 6
        self._DWORD_OF_T_TCOVIEW = 3
        self._DWORD_OF_T_ERRLOG = 8
        self._PRE_IDX_OFFSET = (self._DWORD_OF_T_ERRLOG - 1) * 4
        self._TEST_CASE_MAX = 10
        self._FW_RESULT_ADDRESS = 0
        self._isBusy = False
        self._api_bridge = parent
        self._chip_id = 0
        self._resultSize = 0x2400
        # 利用 ctypes 建立與 C 語言記憶體結構對齊的無號 8 位元整數陣列, 供硬體直接寫入
        self._resultArray = (ctypes.c_uint8 * self._resultSize)(*([0] * self._resultSize))
        self._resultBurstLength = 48
        self._total_reads = self._resultSize // self._resultBurstLength
        self.report_html_dict: dict[int, str] = {}
        self._log("apiReportMgr loaded.")

    def _log(self, message: str) -> None:
        global_log(tag="REPORT_MGR", message=message)

    def _get_report_data(self) -> dict[str, str]:
        """解析硬體回傳的記憶體陣列, 依據 C 結構定義萃取錯誤日誌與狀態"""
        # 取得 tcOview[0].errCnt (用來判斷測試成功或失敗)
        # Header(24 bytes) + tcFreq(4 bytes) + logLastIdx(4 bytes) = 32
        errCnt_bytes = bytes(self._resultArray[32:36])
        errCnt = int.from_bytes(errCnt_bytes, byteorder='little')
        # 判斷 Overall Status (0 = 成功, 非 0 = 錯誤)
        if errCnt == 0:
            overall_status = "<span class='pass'>COMPLETED (PASS)</span>"
        else:
            overall_status = f"<span class='fail'>FAILED (Errors: {errCnt})</span>"
        idx_bytes = bytes(self._resultArray[16:20])
        logUnusedIdx = int.from_bytes(idx_bytes, byteorder='big')
        if logUnusedIdx == 0:
            return {
                "overall_status": overall_status,
                "test_result_content": "<div class='empty-text'>Empty (No test logs generated)</div>"
            }
        header_size = self._DWORD_OF_T_RESULT_HEADER * 4
        tcoview_size = self._DWORD_OF_T_TCOVIEW * self._TEST_CASE_MAX * 4
        errlog_start = header_size + tcoview_size
        parsed_lines: list[str] = []
        for log_idx in range(logUnusedIdx):
            start = errlog_start + (log_idx * self._DWORD_OF_T_ERRLOG * 4)
            end = start + (self._DWORD_OF_T_ERRLOG * 4)
            if end <= len(self._resultArray):
                chunk = self._resultArray[start:end]
                hex_str = " ".join([f"{b:02X}" for b in chunk])
                parsed_lines.append(f"Log Index [{log_idx}]: {hex_str}")
        lines_html = "".join(f"<div class='result-line'>{line}</div>" for line in parsed_lines)
        return {
            "overall_status": overall_status,
            "test_result_content": lines_html if lines_html else "<div class='empty-text'>No errors logged.</div>",
        }

    def _get_mermaid_image(self, syntax: str) -> str:
        """透過 JS 注入呼叫前端瀏覽器引擎渲染 Mermaid, 並利用非同步等待索取 Base64 結果"""
        if self._api_bridge._window:
            try:
                self._log("Invoking JS render...")
                self._api_bridge._window.evaluate_js("window.last_img = null;")
                safe_syntax = json.dumps(syntax)
                self._api_bridge._window.evaluate_js(f"window.renderMermaidToBase64({safe_syntax}).then(res => {{ window.last_img = res; }})")
                time.sleep(0.5)
                img_base64 = self._api_bridge._window.evaluate_js("window.last_img")
                return str(img_base64) if img_base64 else ""
            except Exception as e:
                self._log(f"Error: JS Evaluate: {e}")
        return ""

    # ============================================================================
    # 合併報告功能
    # ============================================================================
    def _combine_reports(self, folder: str, test_board: str, mode: str, test_total: int) -> str:
        """
        將記憶體中的所有單次測試 HTML 剝離外殼後，組合進統一的 Summary 目錄中。
        依據 test_total 遍歷字典，若中間有輪空則跳過該序號。
        """
        self._log(f"Merging reports into Summary Report (Total Expected: {test_total})...")
        toc = [
            '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n',
            f'    <title>Summary Report - {test_board}</title>\n    <style>\n{COMMON_CSS}',
            '        .toc-container { background: #fff; padding: 25px; border-radius: 8px; border-left: 5px solid #28a745; box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin-bottom: 30px; }',
            '        .toc-container h1 { border-bottom: 2px solid #eaeaea; padding-bottom: 15px; margin-top: 0; color: #1e1e1e;}',
            '        .toc-container ul { list-style-type: none; padding-left: 0; }',
            '        .toc-container li { margin-bottom: 15px; font-size: 1.1em; border-left: 3px solid #007acc; padding-left: 10px;}',
            '        .toc-container a { color: #005f9e; text-decoration: none; font-weight: bold; }',
            '        .toc-container a:hover { color: #007acc; text-decoration: underline; }\n    </style>\n</head>\n<body>',
            '    <div class="toc-container" id="top">',
            f'        <h1>📑 Test Summary - {test_board} ({mode} Mode)</h1>\n        <ul>'
        ]
        sections: list[str] = []

        # 依據預期總數遍歷字典，處理輪空情況
        for i in range(1, test_total + 1):
            content = self.report_html_dict.get(i)
            if not content:
                self._log(f"Merge Warning: Index {i} has no data (skipped).")
                continue

            # 擷取 body 內部內容以避免 HTML 頭部定義重疊
            body_start = content.find("<body")
            if body_start != -1:
                body_start = content.find(">", body_start) + 1
            body_end = content.find("</body>")
            inner_content = content[body_start:body_end] if body_start > 0 and body_end != -1 else content
            anchor_id = f"test_case_{i}"
            toc.append(f'            <li><a href="#{anchor_id}">▶ Go to Test Index {i} : Device Verification Report</a></li>')
            sections.append(f'<div id="{anchor_id}">\n{inner_content}')
            sections.append(
                '<div style="text-align: right; margin-top: 10px; margin-bottom: 40px; padding-right: 10px;">'
                '<a href="#top" style="color: #007acc; text-decoration: none; font-weight: bold; '
                'font-size: 1.1em; background: #e9ecef; padding: 8px 15px; border-radius: 5px;">'
                '↑ Back to Top TOC</a></div>\n</div>'
            )

        toc.append('        </ul>\n    </div>')
        merged_content = "\n".join(toc) + "\n" + "\n".join(sections) + "\n</body>\n</html>"
        summary_path = os.path.join(folder, "report_summary.html")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(merged_content)
        return summary_path

    def _gen_report_html(
        self, test_board: str = "", MODE: str = "Binary", project_dir: str = "",
        test_index: int = 1, test_total: int = 1, start_time: str = "",
        overall_status: str = "", test_result_content: str = "", open_browser: bool = True,
        flow_image: str = "", workspaceImageBase64: str = "",
        serial_logs: Optional[list[str]] = None, app_logs: Optional[list[str]] = None,
        test_header_str: str = "", test_content_str: str = ""
    ) -> Optional[str]:
        """填充版型並落檔儲存, 包含關鍵字語法高亮轉換, 同時控制全域流程以決定是否觸發報告合併與彈出瀏覽器動作"""
        try:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not start_time:
                start_time = end_time
            test_time = f"{start_time} ~ {end_time}"
            # --- 處理 Hardware Serial Logs (語法高亮與防破版跳脫) ---
            formatted_serial = []
            if serial_logs:
                for line in serial_logs:
                    safe_line = html.escape(line)
                    if re.search(r'Ro\[\d+\]', safe_line):
                        formatted_serial.append(f'<span style="color: #569CD6;">{safe_line}</span>')
                    else:
                        formatted_serial.append(f'<span style="color: #4ec9b0;">{safe_line}</span>')
            serial_log_str = "\n".join(formatted_serial) if formatted_serial else "No serial logs captured."
            # --- 處理 Application System Logs (語法高亮與防破版跳脫) ---
            formatted_app = []
            if app_logs:
                for line in app_logs:
                    safe_line = html.escape(line)
                    lower_line = safe_line.lower()
                    if 'error' in lower_line or 'exception' in lower_line:
                        formatted_app.append(f'<span style="color: #f48771;">{safe_line}</span>')
                    elif 'warning' in lower_line or 'ignore' in lower_line:
                        formatted_app.append(f'<span style="color: #e5c07b;">{safe_line}</span>')
                    else:
                        formatted_app.append(safe_line)
            app_log_str = "\n".join(formatted_app) if formatted_app else "No application logs captured."
            seq_diag_section = ""
            if workspaceImageBase64:
                seq_diag_section += (
                    '<details style="margin-top: 25px; border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden; '
                    'box-shadow: 0 2px 5px rgba(0,0,0,0.05); background-color: #fff;">\n'
                    '<summary style="background-color: #f8f9fa; padding: 12px 20px; font-size: 1.1em; font-weight: bold; '
                    'color: #2c3e50; cursor: pointer; outline: none; transition: background-color 0.2s;">\n'
                    '🧩 Workspace Layout Image <span style="font-size: 0.85em; color: #888; font-weight: normal; margin-left: 10px;">(Click to Expand)</span>\n'
                    '</summary>\n<div style="text-align: center; padding: 20px; border-top: 1px solid #d1d5db; background-color: #ffffff;">\n'
                    f'<img src="{workspaceImageBase64}" alt="Workspace Image" style="max-width: 100%; height: auto; '
                    'border: 1px solid #eaeaea; border-radius: 6px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">\n</div>\n</details>\n'
                )
            if flow_image:
                seq_diag_section += (
                    '<details style="margin-top: 25px; border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden; '
                    'box-shadow: 0 2px 5px rgba(0,0,0,0.05); background-color: #fff;">\n'
                    '<summary style="background-color: #f8f9fa; padding: 12px 20px; font-size: 1.1em; font-weight: bold; '
                    'color: #2c3e50; cursor: pointer; outline: none; transition: background-color 0.2s;">\n'
                    '📊 Test Sequence Diagram <span style="font-size: 0.85em; color: #888; font-weight: normal; margin-left: 10px;">(Click to Expand)</span>\n'
                    '</summary>\n<div class="sequence-container" style="border-top: 1px solid #d1d5db; padding: 20px; background-color: #ffffff;">\n'
                    f'<img src="{flow_image}" alt="Test Sequence Diagram" class="sequence-img" style="border: 1px solid #eaeaea; '
                    'border-radius: 6px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">\n</div>\n</details>\n'
                )
            header_html = (
                '<details style="margin-top: 25px; border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); background-color: #fff;">\n'
                '<summary style="background-color: #f8f9fa; padding: 12px 20px; font-size: 1.1em; font-weight: bold; color: #2c3e50; cursor: pointer; outline: none;">\n'
                '📄 Test Header (Script) <span style="font-size: 0.85em; color: #888; font-weight: normal; margin-left: 10px;">(Click to Expand)</span>\n'
                f'</summary>\n<div style="padding: 20px; border-top: 1px solid #d1d5db; background-color: #ffffff;">\n<div class="terminal-log">{test_header_str}</div>\n</div>\n</details>'
            ) if test_header_str else ""
            content_html = (
                '<details style="margin-top: 25px; border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); background-color: #fff;">\n'
                '<summary style="background-color: #f8f9fa; padding: 12px 20px; font-size: 1.1em; font-weight: bold; color: #2c3e50; cursor: pointer; outline: none;">\n'
                '📄 Test Content (Binary Data / Script) <span style="font-size: 0.85em; color: #888; font-weight: normal; margin-left: 10px;">(Click to Expand)</span>\n'
                f'</summary>\n<div style="padding: 20px; border-top: 1px solid #d1d5db; background-color: #ffffff;">\n<div class="terminal-log">{test_content_str}</div>\n</div>\n</details>'
            ) if test_content_str else ""
            folder = project_dir if project_dir else os.getcwd()
            os.makedirs(folder, exist_ok=True)
            filled_html = TEMPLATE_REPORT_HTML.format(
                css_styles=COMMON_CSS, test_board=test_board, MODE=MODE, test_index=test_index,
                test_total=test_total, folder=folder, test_time=test_time, overall_status=overall_status,
                test_result_content=test_result_content, sequence_diagram_section=seq_diag_section,
                serial_logs=serial_log_str, app_logs=app_log_str, test_header_section=header_html,
                test_content_section=content_html
            )
            # --- 核心修改：存入字典以保留 Index 資訊 ---
            if test_index == 1:
                self.report_html_dict.clear()
            self.report_html_dict[test_index] = filled_html

            filepath = os.path.join(folder, f"report{test_index}_{test_board}{MODE}.html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(filled_html)
            # 無論是單測或批次, 只要跑到該批次的最後一個索引 (test_index == test_total), 一律觸發總結與彈窗
            if test_index == test_total:
                summary_path = self._combine_reports(folder, test_board, MODE, test_total)
                if summary_path and open_browser:
                    self._log(f"Opening report in browser: {os.path.basename(summary_path)}")
                    file_url = Path(os.path.abspath(summary_path)).as_uri()
                    threading.Thread(target=lambda: webbrowser.open(file_url), daemon=True).start()
            return filepath
        except Exception as e:
            self._log(f"Error: Report Generation Failed: {e}")
            return None

# Interface ---------------------------------------------------------------------------------------------
    def generate_report(
        self, board_id: int = 1, test_mode: int = 0, _workspace_data: Optional[dict[str, Any]] = None,
        _project_dir: str = "", _test_index: int = 1, _test_total: int = 1,
        serial_logs: Optional[list[str]] = None, _workspace_image_base64: str = "",
        app_logs_list: Optional[list[str]] = None
    ) -> int:
        """收集軟硬體日誌與圖表資料, 打包並轉拋至報告渲染層"""
        try:
            if not self._api_bridge or not getattr(self._api_bridge._venus_mgr, '_dev_mgr', None):
                raise RuntimeError("test board is NULL")
            if self._isBusy:
                raise RuntimeError("is Busy")
            self._isBusy = True
            MODE = "Binary" if test_mode == 0 else "Script"
            if board_id == 1:
                test_board = "MCU"
                self._chip_id = 0xBC
                self._FW_RESULT_ADDRESS = 0xC00
                report_data = {
                    "overall_status": "<span class='pass'>COMPLETED</span>",
                    "test_result_content": "<div class='empty-text'>Serial Logged</div>"
                }
            elif board_id == 2:
                test_board = "ATB"
                self._chip_id = 0x48
                self._FW_RESULT_ADDRESS = 0x4000
                if test_mode != 0:
                    raise RuntimeError(f"{test_board} does not support Script Test::{test_mode}")
                self._resultArray = self._api_bridge._venus_mgr._atb_mgr.readTestResult()
                report_data = self._get_report_data()
            else:
                raise RuntimeError(f"Unknown test_board. board_id is {board_id}")
            self._log(f"generate_report():: Process test_board::{test_board} MODE::{MODE}")
            img_base64 = ""
            test_header = ""
            test_content = ""
            if _workspace_data is not None:
                test_header = str(_workspace_data.get("test_header", ""))
                test_content = str(_workspace_data.get("test_content", ""))
                # 準備 Mermaid 語法 (使用 ir_data)
                # ir_data = _workspace_data.get("ir_data", {})
                # if ir_data:
                #     seq_gen = SequenceGen()
                #     mermaid_syntax = seq_gen.generate_syntax(ir_data)
                #     img_base64 = self._get_mermaid_image(mermaid_syntax)
            # 讀取硬體結果陣列
            if test_mode == 0:
                self._resultArray = self._api_bridge._venus_mgr._dev_mgr.readTestResult()
                report_data = self._get_report_data()
            else:
                report_data = {
                    "overall_status": "<span class='pass'>COMPLETED</span>",
                    "test_result_content": "<div class='empty-text'>Serial Logged</div>"
                }
            # 傳遞至統一格式化函式
            self._gen_report_html(
                test_board=test_board, MODE=MODE, project_dir=_project_dir, test_index=_test_index,
                test_total=_test_total, start_time=self._api_bridge._start_time or "",
                overall_status=report_data.get("overall_status", "Unknown"),
                test_result_content=report_data.get("test_result_content", ""),
                flow_image=img_base64, workspaceImageBase64=_workspace_image_base64,
                serial_logs=serial_logs, app_logs=app_logs_list, test_header_str=test_header,
                test_content_str=test_content
            )
            return 0
        except Exception as e:
            self._log(f"Error: generate_report(): {e}")
            return -1
        finally:
            self._isBusy = False


class SequenceGen:
    """負責遞迴解析積木中介碼 (IR), 並轉譯為 Mermaid.js 的循序圖 (Sequence Diagram) 語法"""
    def __init__(self) -> None:
        self._unhandled_types: set[str] = set()
        self._procedures: dict[str, list[dict[str, Any]]] = {}

    def _log(self, message: str) -> None:
        global_log(tag="SEQUENCE_GEN", message=message)

    def generate_syntax(self, ir_data: dict[str, Any]) -> str:
        """掃描全域積木結構, 定位入口點與函式定義區塊後開始主轉譯迴圈"""
        lines = [
            "sequenceDiagram",
            "    autonumber",
            "    participant HOST as TESTBOARD (Host)",
            "    participant DEV as DEVICE (Board)"
        ]
        all_blocks: list[dict[str, Any]] = ir_data.get("Blocks", [])
        self._procedures = {
            str(b.get("name")): b.get("inputs", [])
            for b in all_blocks if b.get("type") == "procedures_defnoreturn"
        }
        startup_block = next((b for b in all_blocks if b.get("type") == "startup"), None)
        if startup_block:
            self._log("Found startup block, starting sequence generation...")
            lines.extend(self._process_blocks(startup_block.get("inputs", [])))
        else:
            self._log("Warning: No startup block found! Parsing non-definition blocks.")
            main_flow = [b for b in all_blocks if b.get("type") != "procedures_defnoreturn"]
            lines.extend(self._process_blocks(main_flow))
        return "\n".join(lines)

    def _process_blocks(self, blocks: list[dict[str, Any]]) -> list[str]:
        """利用反射機制 (getattr) 依據 block type 動態呼叫對應的指令處理器"""
        lines: list[str] = []
        if not blocks:
            return lines
        for block in blocks:
            if not isinstance(block, dict):
                continue
            b_type = block.get("type", "")
            handler_name = f"_handle_{b_type}"
            if hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                lines.extend(handler(block))
            else:
                if b_type not in self._unhandled_types:
                    self._unhandled_types.add(b_type)
                    self._log(f"Unhandled block type: {b_type}")
        return lines

    # ==========================================
    # --- 核心積木處理器 (硬體互動) ---
    # ==========================================
    def _handle_write_device(self, block: dict[str, Any]) -> list[str]:
        return [f"    HOST->>DEV: Write {block.get('dev_id', '??')} [0x{block.get('address', '??')}]"]

    def _handle_read_device(self, block: dict[str, Any]) -> list[str]:
        return [f"    DEV-->>HOST: Read {block.get('dev_id', '??')} [0x{block.get('addr', '??')}]"]

    def _handle_delay(self, block: dict[str, Any]) -> list[str]:
        return [f"    Note over HOST: Delay {block.get('time', 0)} {block.get('time_unit', 'ms')}"]

    def _handle_run_txt(self, block: dict[str, Any]) -> list[str]:
        return [f"    Note over HOST, DEV: Run Script: {block.get('txt', 'script')}"]

    def _handle_print(self, block: dict[str, Any]) -> list[str]:
        val_safe = str(block.get('val', '')).replace('\n', '\\n').replace('$', '').replace('"', "'")
        return [f"    Note right of HOST: print: {val_safe}"]

    def _handle_abort(self, _block: dict[str, Any]) -> list[str]:
        return ["    Note over HOST, DEV: << TEST ABORTED >>"]

    # ==========================================
    # --- 流程控制處理器 ---
    # ==========================================
    def _handle_procedures_callnoreturn(self, block: dict[str, Any]) -> list[str]:
        """攔截函式呼叫, 查表並遞迴渲染內部邏輯以維持循序圖連貫性"""
        func_name = str(block.get("extraState", {}).get("name", ""))
        if func_name in self._procedures:
            return self._process_blocks(self._procedures[func_name])
        return [f"    Note over HOST: Unknown function: {func_name}"]

    def _handle_controls_if_custom(self, block: dict[str, Any]) -> list[str]:
        lines = ["    alt Condition Check"]
        do_flow: list[dict[str, Any]] = []
        else_flow: list[dict[str, Any]] = []
        for inp in block.get("inputs", []):
            if "do" in inp:
                do_flow = [inp["do"]] if isinstance(inp["do"], dict) else inp["do"]
            if "else" in inp:
                else_flow = [inp["else"]] if isinstance(inp["else"], dict) else inp["else"]
        lines.extend(self._process_blocks(do_flow))
        if else_flow:
            lines.append("    else")
            lines.extend(self._process_blocks(else_flow))
        lines.append("    end")
        return lines

    def _handle_controls_repeat_ext_ex(self, block: dict[str, Any]) -> list[str]:
        lines = [f"    loop {block.get('times', '?')} times"]
        lines.extend(self._process_blocks(block.get("inputs", [])))
        lines.append("    end")
        return lines

    def _handle_wait_until_timeout(self, block: dict[str, Any]) -> list[str]:
        lines = [f"    opt Wait for {block.get('event', 'event')}"]
        do_flows: list[dict[str, Any]] = []
        for inp in block.get("inputs", []):
            if "f_do" in inp:
                content = inp["f_do"]
                if isinstance(content, dict):
                    do_flows.append(content)
                else:
                    do_flows.extend(content)
        lines.extend(self._process_blocks(do_flows))
        lines.append("    end")
        return lines

    # --- 忽略不需要顯示在序列圖上的輔助積木 ---
    def _handle_set_var(self, _block: dict[str, Any]) -> list[str]:
        return []

    def _handle_loop_control(self, _block: dict[str, Any]) -> list[str]:
        return ["    Note over HOST: break loop"]

    def _handle_return_void(self, _block: dict[str, Any]) -> list[str]:
        return ["    Note over HOST: return"]
