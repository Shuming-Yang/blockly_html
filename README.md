# Device Verification Tool with Blockly GUI

---

- [Device Verification Tool with Blockly GUI](#device-verification-tool-with-blockly-gui)
- [Project File List](#project-file-list)

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
│  │       ├── ovvenus.py        # [模組] VENUS 硬體行為調用DLL API
│  │       ├── ovusb.py          # [底層] DLL 調用層
│  │       ├── atbcfg_mgr.py     # [任務] ATB Configuration 邏輯區
│  │       ├── gens_data.py      # [資源] Gens Application 資源區
│  │       ├── gens_mgr.py       # [任務] Gens Application 邏輯區
│  │       ├── cases_mgr.py      # [任務] 轉譯 Hex 與下載邏輯
│  │       ├── parse_mgr.py      # [任務] Blockly 解析邏輯
│  │       ├── cfg_mgr.py        # [任務] 後端配置
│  │       ├── report_mgr.py     # [任務] 產生測試報告
│  │       ├── fw_bin.py         # [資源] ATB Firmware Binary 資料
│  │       ├── gens/             # [任務] Gens 邏輯區
│  │       └── resource/         # [資源] 靜態文件、預設設定檔、圖片
│  ├─ blockly                    # [frontend 子資料夾] Blockly 官方函式庫 v12.3.1
│  ├─ mermaid                    # [frontend 子資料夾] Mermaid 渲染器(離線版)
│  └─ script                     # [frontend 子資料夾] 客製化前端程式碼
│     ├─ index.js                # [新增] UI 初始化與 pywebview 呼叫邏輯
│     ├─ python_custom.js        # [新增] Blockly 積木轉換
│     └─ flowchart.js            # [新增] JSON 轉為 Mermaid 語法的邏輯 (To-Do)
├─ build                         # [資源] CMAKE產生的編譯環境
├─ release                       # [Target] Compiled output
│  ├─ oneDir                     # [Target] One Directory 打包模式
|  ├─ oneFile                    # [Target] One File 打包模式
|  ├─ DevVerifyGUI.vsix          # [Target] 打包成Vsix作為VSCODE套件安裝
|  ├─ DevVerifyGUI_Setup.exe     # [Target] 基於One Directory模式後處理打包成安裝執行檔
│  ├─ DevVerifyGUI.zip           # [Target] 將One Directory模式後處理打包成ZIP (Pending: Update terminated)
│  └─ mcu_i3c_beta.hex           # [Target] 對應的MCU HEX Binary檔案
├─ tools                         # [工具] 工具資源
|  ├─ nsis_bin                   # [工具]　建置安裝檔工具
|  ├─ cleanup.py                 # [工具]　Clean workspace
|  └─ bin2py.py                  # [工具]　將binary檔案資料轉為Python data
├─ media                         # [資源] 多媒體資源
│  └─ applicationArch.png        # [資源] Architecture Top View of Application
├─ py_exe                        # [資源] 打包用資源
│  └─ icon.ico                   # [資源] 用以打包成執行檔ICON
└─ vscode_ext                    # [資源] VS Code Extension 專案區 (Pending: Update terminated)
   ├─ .gitignore
   ├─ CHANGELOG.md
   ├─ eslint.config.mjs
   ├─ extension.js
   ├─ icon.ico
   ├─ icon.png
   ├─ jsconfig.json
   ├─ LICENSE.md
   ├─ package-lock.json
   ├─ package.json
   └─ README.md
```

