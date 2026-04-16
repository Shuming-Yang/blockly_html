# Device Verification Tool with Blockly GUI

---

- [Device Verification Tool with Blockly GUI](#device-verification-tool-with-blockly-gui)
- [Project File List](#project-file-list)
- [GitLab Commit 與 Issue 聯動規範](#gitlab-commit-與-issue-聯動規範)
  - [GitLab 議題 (Issue) 聯動關鍵字](#gitlab-議題-issue-聯動關鍵字)
  - [1. 格式範本](#1-格式範本)
  - [2. 常用關鍵字](#2-常用關鍵字)
  - [3. 範例 (Example)](#3-範例-example)
  - [4. 工具操作說明](#4-工具操作說明)
- [GitLab 進階管理規範： Tags, Milestones 的協作邏輯](#gitlab-進階管理規範-tags-milestones-的協作邏輯)
  - [1. 標籤 (Tags) 使用規則](#1-標籤-tags-使用規則)
  - [2. 里程碑 (Milestones)](#2-里程碑-milestones)
  - [3. 快速操作 (Quick Actions)](#3-快速操作-quick-actions)
- [VS Code 提交訊息格式化工具 (Commit Message Editor)](#vs-code-提交訊息格式化工具-commit-message-editor)
  - [安裝必備套件 (僅限 VS Code 使用者)](#安裝必備套件-僅限-vs-code-使用者)
  - [工具操作步驟](#工具操作步驟)
  - [非 VS Code 使用者規範 (手動輸入指南)](#非-vs-code-使用者規範-手動輸入指南)

---

# Project File List

```txt
LOCAL_blockly_html
├─ CMakeLists.txt                # [CMAKE] Build Target
├─ README.txt                    # [說明] README
├─ application                   # 這裡是應用程式的核心 同時預設為frontend的root資料夾
│  ├── index.py                  # [啟動點] 建立視窗、綁定 Api 物件
│  ├── index.html                # [主視覺] 視窗GUI
│  ├── backend/                  # [backend 資料夾]
│  │   ├── lib/                  # [底層] DLL底層驅動
│  │   └── src/                  # [核心邏輯包] 增加 __init__.py 變成 Package
│  │       ├── __init__.py       # 使 src 成為可被 import 的 package
│  │       ├── api_bridge.py     # [入口] 專門提供給index.py去對接 JS 的 Interface, API 入口類別 (ApiBridge)，串接所有模組
│  │       ├── ovatb.py          # [模組] ATB   硬體行為調用DLL API
│  │       ├── ovmcu.py          # [模組] MCU   硬體行為調用DLL API
│  │       ├── ovvenus.py        # [模組] VENUS 硬體行為調用DLL API - 同時作為ATB 與 MCU 的API調用者
│  │       ├── ovusb.py          # [底層] DLL 調用層
│  │       ├── DevVerifyGUI.ini  # [資源] 產生Script測試 設定FPGA/BA/TITAN規則定義
│  │       ├── gens_data.py      # [資源] Gens Application 資源區
│  │       ├── gens_mgr.py       # [任務] Gens Application 邏輯區
│  │       ├── cases_mgr.py      # [任務] 轉譯 Hex 與下載邏輯
│  │       ├── parse_mgr.py      # [任務] Blockly 解析邏輯產生IR資料
│  │       ├── cfg_mgr.py        # [任務] 後端配置管理員
│  │       ├── report_mgr.py     # [任務] 產生測試報告
│  │       ├── fw_bin.py         # [資源] ATB Firmware Binary 資料
│  │       ├── shared_utils.py   # [任務] 共用工具程式集(不可import 其他的porject模塊)
│  │       ├── stream_mgr.py     # [任務] 影像資料管理員
│  │       ├── gens/             # [任務] Gens 邏輯區
│  │       └── resource/         # [資源] 靜態文件、預設設定檔、圖片
│  ├─ blockly                    # [frontend 子資料夾] Blockly 官方函式庫 v12.3.1
│  ├─ mermaid                    # [frontend 子資料夾] Mermaid 渲染器(離線版)
│  └─ script                     # [frontend 子資料夾] 客製化前端程式碼
│     ├─ index.js                # [任務] UI 初始化與 pywebview 呼叫邏輯
│     ├─ python_custom.js        # [任務] Blockly 積木轉換
│     ├─ python_custom.js        # [任務] Blockly 產生IR資料
│     └─ flowchart.js            # [任務] JSON 轉為 Mermaid 語法的邏輯 (To-Do)
├─ build                         # [資源] CMAKE產生的編譯環境
├─ release                       # [Target] Compiled output
│  ├─ oneDir                     # [資源] One Directory 打包模式
|  ├─ oneFile                    # [Target] One File 打包模式 - 停止更新
|  ├─ DevVerifyGUI.vsix          # [Target] 打包成Vsix作為VSCODE套件安裝 - 停止更新
|  ├─ DevVerifyGUI_Setup.exe     # [Target] 基於One Directory模式後處理打包成安裝執行檔
│  ├─ DevVerifyGUI.zip           # [Target] 將One Directory模式後處理打包成ZIP (Pending: Update terminated) - 停止更新
│  ├─ fpga_autotest.hex          # [資源] 支援Script完整功能的MCU HEX Binary檔案
│  └─ mcu_i3c_beta.hex           # [資源] 支援Binary與舊的Script功能的MCU HEX Binary檔案
├─ tools                         # [工具] 工具資源
|  ├─ ninja                      # [工具]　建置Make檔案工具
|  ├─ nsis_bin                   # [工具]　建置安裝檔工具
|  ├─ cleanup_extensions.py      # [工具]　清除未列在建議列表中的VSCode擴充套件
|  ├─ cleanup.py                 # [工具]　Clean workspace
|  └─ bin2py.py                  # [工具]　將binary檔案資料轉為Python data
├─ media                         # [資源] 多媒體資源
│  └─ applicationArch.png        # [資源] Architecture Top View of Application
├─ py_exe                        # [資源] pyinstaller 打包用資源
└─ vscode_ext                    # [資源] VS Code Extension 打包用資源
```

---

# GitLab Commit 與 Issue 聯動規範

## GitLab 議題 (Issue) 聯動關鍵字

透過在 Commit Message 中加入以下關鍵字，可以自動化管理 Issue 狀態：

| 動作類別 | 常用關鍵字 (不分大小寫) | GitLab 觸發效果 |
| :--- | :--- | :--- |
| **自動關閉** | `Fix`, `Fixes`, `Fixed`<br>`Close`, `Closes`, `Closed`<br>`Resolve`, `Resolves`, `Resolved` | 當 Commit 推送到 **main** 分支後，指定的 Issue 會自動變更為 **Closed** 狀態。 |
| **純引用 / 連結** | 直接輸入 `#Issue編號`<br>(例如：`#123`) | 在 Issue 的留言板自動產生該 Commit 的連結與紀錄，但 **不會變更** Issue 的開關狀態。 |
| **跨專案關聯** | `群組名/專案名#編號` | 如果你的代碼在 A 專案，但想關聯 B 專案的 Issue，請使用此完整格式。 |

> **💡 注意事項：**
> 1. 關鍵字與 `#` 之間建議保留一個空格（例如：`Fix #123`）。
> 2. 自動關閉功能僅在 Commit 進入「預設分支」（通常是 `main`）時才會生效。

---

為了自動化追蹤開發進度，請大家在 Commit 時遵循以下格式：

## 1. 格式範本
[標題：簡述做了什麼]
[描述：詳細說明或解決了什麼問題] 關鍵字 #Issue編號

## 2. 常用關鍵字
- **關閉議題：** `Fixes #ID` 或 `Closes #ID` (當此 Commit 完成了該任務時使用)
- **關聯議題：** 直接打 `#ID` (當只是部分更新，不需關閉議題時使用)

## 3. 範例 (Example)
- **繁中：** 修復後端 API 錯誤。 Fixes #12
- **簡中：** 修复后端 API 错误。 Fixes #12
- **EN：** Fix backend API error. Fixes #12
- *多語言範例 (繁中/簡中/英文)*
  1. 自動關閉議題 (適用於任務完成時)
  當你把這段代碼推送到 main 分支，該 Issue 就會自動結案。
     - 繁體中文 (TW)
     標題：修復 #123 修正 I2C 讀取超時問題
     描述：此更新優化了 Python 後端的通訊邏輯，解決了 VENUS 設備無回應的情況。
     - 简体中文 (CN)
     标题：修复 #123 修正 I2C 读取超时问题
     描述：此更新优化了 Python 后端的通讯逻辑，解决了 VENUS 设备无响应的情况。
     - English (EN)
     Title: Fix #123 Correct I2C read timeout issue
     Description: This update optimizes the Python backend logic and resolves the VENUS device non-response issue.
  2. 純引用議題 (適用於部分完成或過程記錄)
  如果你只是更新了一部分，或是想讓這筆 Commit 跟某個討論關聯，但不希望關閉它。
     - 繁體中文 (TW)
     標題：處理 #45 調整 HTML 介面佈局
     描述：目前僅完成按鈕樣式修改，後續邏輯將在下一筆 Commit 補上。
     - 简体中文 (CN)
     标题：处理 #45 调整 HTML 界面布局
     描述：目前仅完成按钮样式修改，后续逻辑将在下一笔 Commit 补上。
     - English (EN)
     Title: Work on #45 Adjust HTML UI layout
     Description: Only button styles are modified. The remaining logic will be added in the next commit.
- *註：請確保編號前有 # 字號，且關鍵字與編號間有一個空格。*

## 4. 工具操作說明
- **GitHub Desktop 使用者**
  - 「Summary (Required)」 = 標題
  - 「Description」 = 描述
  - 在左下角的 "Summary (required)" 欄位輸入「標題」。
  - 在下方較大的 "Description" 欄位輸入「描述」（包含關鍵字如 Fixes #123）。
  - 點擊 "Commit to main"，然後點擊右上角的 "Push origin"。
- **TortoiseGit 使用者**
  - 對話框中的第一行內容 = 標題
  - 按下 Enter 換行後的內容 = 描述
  - 在資料夾點擊右鍵選擇 "Git Commit -> 'main'..."。
  - 在彈出的視窗中，Message 框的第一行即為「標題」。
  - 按下 Enter 兩次後，開始輸入「描述」（包含關鍵字）。
  - 勾選左下角的檔案後點擊 "Commit"，接著在完成視窗點擊 "Push"。

---

# GitLab 進階管理規範： Tags, Milestones 的協作邏輯

為了更好地追蹤專案進度，這個專案目前引入GitLab預設的標籤與里程碑管理系統。

## 1. 標籤 (Tags) 使用規則
* **~"v"**: 軟體版本與專案Milestone對應標籤
* 擴充選項: **~"Type::Bug"**: 程式報錯或硬體通訊異常。
* 擴充選項: **~"Type::Feature"**: 新功能開發（如：HTML 新介面）。
* 擴充選項: **~"Component::I2C"**: 涉及 VENUS 設備或 I2C 協議的改動。

## 2. 里程碑 (Milestones)
* 請務必將每個 **議題** 與 **標籤** 關聯到當前的 **Milestone**，以便在看板 (Board) 檢視進度。
* 可以透過當前的 **Milestone** 查詢到所有的標籤, 以及關聯的議題跟其他標籤
* 議題內容關連到對應的JIRA連結, 所有的細節更新在JIRA上, 在IT未協助整合JIRA跟GitLab之前, 以議題來串連JIRA

## 3. 快速操作 (Quick Actions)
在 Issue 留言區或 MR 描述區使用以下指令：
* 分配任務：`/assign @帳號`
* 設定標籤：`/label ~"標籤名"`
* 關聯里程碑：`/milestone %"里程碑名"`

*提示：在 GitLab 介面輸入 `/` 即可看到所有可用指令。*

---

# VS Code 提交訊息格式化工具 (Commit Message Editor)

為了確保團隊協作時的 Commit 歷史紀錄清晰易讀，本專案已在 `.vscode/settings.json` 中內建了自動化的 Commit 格式設定。只要安裝指定的擴充套件，即可透過圖形化表單輕鬆產生符合規範（`[標籤] 描述`）的提交訊息。

## 安裝必備套件 (僅限 VS Code 使用者)
請在 VS Code 的擴充功能 (Extensions) 搜尋並安裝以下套件：
* **套件名稱：** `Git Commit Message Editor`
* **識別碼：** `adam-bender.commit-message-editor`
*(註：安裝後無須進行任何額外設定，專案會自動載入專屬規則)*

## 工具操作步驟
1. 進入 VS Code 左側的 **原始檔控制 (Source Control)** 面板。
2. 在填寫 Commit 訊息的輸入框上方，點擊 **「編輯器圖示 (小鉛筆或對話框圖案)」**。
3. 畫面將預設開啟表單 (Form) 介面，請依序填寫：
   * **Prefix Type (前綴標籤)：** 從下拉選單中，根據你修改的檔案類型選擇對應標籤（介面上會提示各標籤適用的檔案，例如 `*.py` 請選 `[BACKEND]`）。
   * **Subject (主旨)：** 請輸入簡短的英文修改描述（例如：`Fine tune code alignment`）。
   * **Body (正文 - 選填)：** 若有詳細修改說明，或需要使用 GitLab 聯動關鍵字（如 `Fixes #123`），請填寫於此。若無則直接留空，系統將自動略過。
4. 填寫完畢後點擊 **Save (儲存)**，符合規範的文字將會自動填入 Git 面板中。
5. 最後點擊「提交 (Commit)」即可。

## 非 VS Code 使用者規範 (手動輸入指南)
若你習慣使用 GitHub Desktop、TortoiseGit 或原生終端機指令，請參考以下標籤規範，手動在 Commit 標題前方加入對應的前綴（包含中括號與一個半形空格）：

| 前綴標籤 | 適用檔案與修改範圍 |
| :--- | :--- |
| `[BACKEND]` | 所有 `.py` Python 後端檔案 |
| `[GUI]` | 所有 `.html`, `.css`, `.js` 前端介面檔案 |
| `[CMAKE]` | 所有 `.cmake` 檔案與 `cmakelists.txt` |
| `[BLOCKLY]` | 路徑包含 `application/blockly/*` |
| `[MERMAID]` | 路徑包含 `application/mermaid/*` |
| `[MEDIA]` | 路徑包含 `application/media/*` |
| `[RELEASE]` | 路徑包含 `release/*.exe` (執行檔更新) |
| `[DOCS]` | 路徑包含 `doc/*` (文件更新) |
| `[TOOLS]` | 路徑包含 `tools/*` (工具鏈更新) |
| `[GIT]` | `.gitignore`, `.gitattributes` 等 Git 設定檔 |
| `[VSCODE]` | 路徑包含 `.vscode/*` 的編輯器設定 |

**手動輸入格式範例：**
```text
[BACKEND] Fix I2C read timeout issue

This update optimizes the stream_mgr.py logic.
Fixes #123
```

---
