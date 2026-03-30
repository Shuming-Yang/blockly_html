CMAKE_MINIMUM_REQUIRED(VERSION 3.19)

# 設定 index.py 的路徑 (如果跟 CMakeLists.txt 在同一層，就直接這樣寫)
SET(INDEX_FILE "${CMAKE_CURRENT_SOURCE_DIR}/application/index.py")
# 將整個 index.py 讀進 CMake 變數中
FILE(READ "${INDEX_FILE}" INDEX_CONTENT)
# 利用正則表達式精準抓取 APP_VERSION = "0.0.1.4"
string(REGEX MATCH "APP_VERSION[ \t]*=[ \t]*[\"']([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)[\"']" _ ${INDEX_CONTENT})
SET(EXTRACTED_VERSION ${CMAKE_MATCH_1})
# 防呆機制
if(NOT EXTRACTED_VERSION)
    MESSAGE(WARNING "Could not parse APP_VERSION from index.py! Using default 0.0.0.0")
    SET(EXTRACTED_VERSION "0.0.0.0")
endif()
# 將抓到的版本號塞給 CMake Project
PROJECT(GuiTestCmdTool VERSION ${EXTRACTED_VERSION})
MESSAGE(STATUS "🌟 Project:${PROJECT_NAME}, Revision:${PROJECT_VERSION}")

SET(CMAKE_VERBOSE_MAKEFILE FALSE CACHE STRING "Verbose" FORCE)  # CMAKE除錯啟動/關閉
# 確保編譯日誌以純文字形式輸出 而不會包含任何 ANSI 顏色代碼 這在不支援顏色輸出的終端機或日誌系統中可以避免亂碼
SET(CMAKE_COLOR_MAKEFILE OFF CACHE STRING "Output Log Color" FORCE)
# 告訴 CMake 生成一個名為 compile_commands.json 的檔案
# 他是一個標準化的 JSON 格式檔案 包含了專案中所有編譯指令的詳細清單
# 這個清單會列出每個原始碼檔案 例如 .c, .cpp 是如何被編譯的
SET(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE STRING "Export compile commands" FORCE)

SET(EXT "")
IF(WIN32)
    SET(EXT ".exe")
ENDIF()

# =============================================================
# 環境檢測與相依性安裝 (DEPENDENCY CHECK & INSTALL)
# =============================================================

# 尋找 Node.js
FIND_PROGRAM(NODE_EXECUTABLE NAMES node node${EXT})
# 預設不開啟 VSIX 打包
SET(ENABLE_VSIX_PACKAGING FALSE)
IF(NODE_EXECUTABLE)
    MESSAGE(STATUS "✅ Found Node.js: ${NODE_EXECUTABLE}")
    # 尋找 NPM
    IF(WIN32)
        FIND_PROGRAM(NPM_EXECUTABLE NAMES npm.cmd npm)
    ELSE()
        FIND_PROGRAM(NPM_EXECUTABLE NAMES npm)
    ENDIF()
    IF(NPM_EXECUTABLE)
        MESSAGE(STATUS "✅ Found NPM: ${NPM_EXECUTABLE}")
        # 尋找 VSCE
        IF(WIN32)
            FIND_PROGRAM(VSCE_EXECUTABLE NAMES vsce.cmd vsce)
        ELSE()
            FIND_PROGRAM(VSCE_EXECUTABLE NAMES vsce)
        ENDIF()
        
        IF(NOT VSCE_EXECUTABLE)
            MESSAGE(STATUS "⚠️  'vsce' not found. Attempting to install via npm...")
            EXECUTE_PROCESS(COMMAND "${NPM_EXECUTABLE}" install -g @vscode/vsce RESULT_VARIABLE INSTALL_RESULT)
            IF("${INSTALL_RESULT}" STREQUAL "0")
                MESSAGE(STATUS "✅ 'vsce' installed successfully!")
                # SET(ENABLE_VSIX_PACKAGING TRUE)
            ELSE()
                MESSAGE(WARNING "❌ Failed to install 'vsce'. VSIX packaging will be skipped.")
            ENDIF()
        ELSE()
            MESSAGE(STATUS "✅ Found VSCE: ${VSCE_EXECUTABLE}")
            # SET(ENABLE_VSIX_PACKAGING TRUE)
        ENDIF()
    ELSE()
        MESSAGE(WARNING "⚠️  Node.js found but NPM not found. Cannot check/install vsce.")
    ENDIF()
ELSE()
    MESSAGE(STATUS "⚠️  Node.js NOT found. VSIX packaging will be SKIPPED.")
ENDIF()

# =============================================================
# 設定變數 (VARIABLES)
# =============================================================
SET(EXE_NAME "DevVerifyGUI")
SET(RESOURCE_DIR "${CMAKE_SOURCE_DIR}/application")
SET(PYTHON_SCRIPT "${RESOURCE_DIR}/index.py") 
SET(RELEASE_DIR "${CMAKE_SOURCE_DIR}/release")
SET(VSCODE_EXT_DIR "${CMAKE_SOURCE_DIR}/vscode_ext")
SET(PY_EXE_DIR "${CMAKE_SOURCE_DIR}/py_exe")
SET(APP_ICON "${PY_EXE_DIR}/icon.ico")
SET(APP_README "${PY_EXE_DIR}/README.md")
SET(VENV_DIR "${CMAKE_SOURCE_DIR}/.venv")
SET(VENV_PYTHON "${VENV_DIR}/Scripts/python${EXT}")
SET(VENV_PIP "${VENV_DIR}/Scripts/pip${EXT}")
# =============================================================
# 設定專案內建的 NSIS (PORTABLE NSIS CONFIG)
# =============================================================
# 直接指定專案內部的 NSIS 編譯器路徑
SET(LOCAL_MAKENSIS "${CMAKE_SOURCE_DIR}/tools/nsis_bin/makensis.exe")
# 檢查檔案是否存在 (防呆)
IF(EXISTS "${LOCAL_MAKENSIS}")
    MESSAGE(STATUS "✅ Found Portable NSIS in repository: ${LOCAL_MAKENSIS}")    
    # 強制 CPack 使用指定的 NSIS，而不是系統安裝的
    SET(CPACK_NSIS_EXECUTABLE "${LOCAL_MAKENSIS}")
    # 把這個路徑加入 CMake 的搜尋提示
    LIST(APPEND CMAKE_PROGRAM_PATH "${CMAKE_SOURCE_DIR}/tools/nsis_bin")
ELSE()
    MESSAGE(FATAL_ERROR "Portable NSIS not found at ${LOCAL_MAKENSIS}. Please ensure the 'tools/nsis_bin' folder is committed to Git.")
ENDIF()
# =============================================================
# 安裝與打包設定 (INSTALL & CPACK)
# =============================================================
# =============================================================
# 動態產生 PyInstaller 的 Version File (無須手動維護)
# =============================================================
# 自動取得「今天」的日期
STRING(TIMESTAMP BUILD_YEAR "%Y")
STRING(TIMESTAMP BUILD_MONTH "%m")
STRING(TIMESTAMP BUILD_DAY "%d")
# 消除月份和日期的開頭 0 (例如 "03" 變 "3")，避免 Python 3 報錯
MATH(EXPR BUILD_MONTH_INT "${BUILD_MONTH}")
MATH(EXPR BUILD_DAY_INT "${BUILD_DAY}")
# 組合成 filevers 需要的 Tuple 格式: (2026, 3, 4, 0)
SET(FILEVERS_TUPLE "${BUILD_YEAR}, ${BUILD_MONTH_INT}, ${BUILD_DAY_INT}, 0")
# 同時也組合成字串格式: "2026.03.04.00" (提供給下方 StringStruct 使用)
SET(FILEVERS_STR "${BUILD_YEAR}.${BUILD_MONTH}.${BUILD_DAY}.00")
# 轉換版本號格式 (例如 "0.0.1.4" -> "0, 0, 1, 4") 給 ffi 使用
STRING(REPLACE "." ", " VERSION_TUPLE "${EXTRACTED_VERSION}")
# 設定產生的檔案路徑 (放在 build 目錄下，確保不弄髒原始碼資料夾)
SET(GENERATED_VERSION_FILE "${CMAKE_BINARY_DIR}/pyinstaller_version_info.txt")
# 將 PyInstaller 需要的格式直接寫入檔案，並注入動態變數
FILE(WRITE "${GENERATED_VERSION_FILE}" "# UTF-8
# 宣告檔案的編碼為 UTF-8

# 定義一個 VSVersionInfo 類別，用於描述版本資訊。
VSVersionInfo(
  # 定義一個 FixedFileInfo 類別，用於描述固定檔案資訊。
  ffi=FixedFileInfo(
    # 設定檔案版本 (file version) - 這裡直接改為與產品版本同步
    filevers=(${FILEVERS_TUPLE}),
    # 設定產品版本 (product version)
    prodvers=(${VERSION_TUPLE}),
    # 設定有效位元的遮罩 (bitmask)。
    mask=0x3f,
    # 設定檔案的布林屬性 (Boolean attributes)。
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    # 設定作業系統為 Windows NT。
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    # 設定檔案類型為應用程式。
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    # 設定檔案子類型 (subtype) 為未定義。
    subtype=0x0,
    # Creation date and time stamp.
    # 設定建立日期和時間戳記為 (0, 0)。
    date=(0, 0)
    ),
  # 定義一個列表 kids，用於存放其他類型的版本資訊。
  kids=[
    # 定義一個 StringFileInfo 類別，用於描述字串版本的資訊。
    StringFileInfo(
      [
      StringTable(
        # 語言代碼 (language code)。
        '000004B0',
        [
          # 公司名稱。
          StringStruct('CompanyName', 'OmniVision Technologic, Inc.'),
          # 檔案描述。
          StringStruct('FileDescription', 'Device Verification Tool'),
          # 檔案版本
          # StringStruct('FileVersion', '${FILEVERS_STR}'),
          # 應用程式的內部名稱。
          StringStruct('InternalName', 'Device Verification'),
          # 著作權資訊。
          StringStruct('LegalCopyright', 'Copyright © 2026 OmniVision Technologic, Inc.'),
          # 可執行檔的原始檔名。 (動態帶入 CMake 定義的 EXE_NAME)
          StringStruct('OriginalFilename', '${EXE_NAME}.exe'),
          #產品名稱。
          StringStruct('ProductName', 'Device Verification'),
          # 產品版本, 此處會覆蓋掉prodvers的設定。 (動態帶入版本號)
          StringStruct('ProductVersion', '${EXTRACTED_VERSION}')
        ])
      ]), 
    # 定義一個 VarFileInfo 類別，用於描述可變的檔案資訊。
    # 目前只定義了一個可變的資訊，即翻譯代碼 (Translation) 為 0 和 1200 (可能代表英文)
    VarFileInfo([VarStruct('Translation', [0, 1200])])
  ]
)
")
MESSAGE(STATUS "✅ Dynamically generated PyInstaller version file at: ${GENERATED_VERSION_FILE}")
# 使用 CPACK_INSTALLED_DIRECTORIES 直接指定要打包的資料夾
# 格式：SET(CPACK_INSTALLED_DIRECTORIES "真實來源路徑" "安裝包內的路徑")
# 注意：這裡的來源路徑結尾通常不要加斜線，讓 CPack 自己處理
SET(CPACK_INSTALLED_DIRECTORIES "${RELEASE_DIR}/oneDir" ".")
# CPack 設定：定義安裝程式的外觀與行為
SET(CPACK_GENERATOR "NSIS")
SET(CPACK_PACKAGE_NAME "${EXE_NAME}")
SET(CPACK_PACKAGE_VENDOR "OmniVision")
SET(CPACK_PACKAGE_CONTACT "support@ovt.com")
SET(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
SET(CPACK_PACKAGE_DESCRIPTION_SUMMARY "DevVerifyGUI Application Installer")
SET(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_SOURCE_DIR}/py_exe/SetupLicense.txt") # 指定授權文件路徑
SET(CPACK_PACKAGE_INSTALL_DIRECTORY "${EXE_NAME}")
# 修改安裝根目錄
# 預設是 "$PROGRAMFILES" (C:\Program Files)，改為 "$LOCALAPPDATA"
# 這樣安裝路徑會變成 C:\Users\使用者\AppData\Local\DevVerifyGUI
# 這通常不需要管理員權限即可寫入
SET(CPACK_NSIS_INSTALL_ROOT "$LOCALAPPDATA")
# =============================================================
# 強制寫入 Windows 檔案詳細資料 (File Metadata)
# =============================================================
# VIProductVersion 必須嚴格遵守 "X.X.X.X" 四碼格式 (例如 1.0.0.0)
# 使用字串換行的方式，一次注入多個 NSIS 指令
# 告訴 NSIS：我不需要管理員權限 (RequestExecutionLevel user) 也合併在這裡設定
SET(CPACK_NSIS_DEFINES "
    VIProductVersion '${PROJECT_VERSION}'
    VIAddVersionKey 'ProductName' '${EXE_NAME}'
    VIAddVersionKey 'CompanyName' '${CPACK_PACKAGE_VENDOR}'
    VIAddVersionKey 'LegalCopyright' 'Copyright (C) 2026 ${CPACK_PACKAGE_VENDOR}'
    VIAddVersionKey 'FileDescription' '${CPACK_PACKAGE_DESCRIPTION_SUMMARY}'
    VIAddVersionKey 'FileVersion' '${PROJECT_VERSION}'
    VIAddVersionKey 'ProductVersion' '${PROJECT_VERSION}'
    RequestExecutionLevel user
")
SET(CPACK_PACKAGE_FILE_NAME "${EXE_NAME}_Setup")
# NSIS 特有設定
SET(CPACK_NSIS_DISPLAY_NAME "DevVerifyGUI Tool") # 在「新增/移除程式」裡顯示的名字
SET(CPACK_NSIS_HELP_LINK "")
SET(CPACK_NSIS_MODIFY_PATH OFF) # 選項：是否讓使用者選擇加入環境變數 PATH
# 建立「開始選單」捷徑
SET(CPACK_NSIS_MENU_LINKS "${EXE_NAME}.exe" "DevVerifyGUI")
# 建立最終任務清單 (Python EXE 是必備的)
SET(FINAL_DEPENDENCIES package_exe)

# 預批次處理路徑
SET(ATB_BIN "${CMAKE_SOURCE_DIR}/application/backend/src/resource/fw_atb.bin")
SET(GEN_FW_PY "${CMAKE_SOURCE_DIR}/application/backend/src/fw_bin.py")
SET(CONVERT_SCRIPT "${CMAKE_SOURCE_DIR}/tools/bin2py.py")

IF(NOT EXISTS ${ATB_BIN})
    MESSAGE(WARNING "ATB BIN file not found at ${ATB_BIN}!!!!")
ENDIF()

# 直接尋找系統中第一個符合的 Python
SET(Python3_FIND_REGISTRY FIRST)
set(Python3_FIND_STRATEGY LOCATION)
# 語法 3.8...3.13 需要 CMake 3.19+
# 這樣可以確保如果裝了 3.14，它不會因為 "3.12+" 符合條件就抓錯
MESSAGE(STATUS "🔍 Searching for the first compatible Python (3.8 <= version < 3.14)...")
# Development會強制與GCC版本相符
FIND_PACKAGE(Python3 3.8...<3.14  COMPONENTS Interpreter Development REQUIRED)

# 檢查是否為 64-bit Python
EXECUTE_PROCESS(
    COMMAND "${Python3_EXECUTABLE}" -c "import struct; print(struct.calcsize('P') * 8)"
    OUTPUT_VARIABLE PYTHON_ARCH
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

IF(Python3_FOUND)
    MESSAGE(STATUS "✅ 成功鎖定 Python: ${Python3_EXECUTABLE} (v${Python3_VERSION})")
    # 驗證位元數
    IF("${PYTHON_ARCH}" STREQUAL "64")
        MESSAGE(STATUS "✅ Architecture: 64-bit (Pass)")
    ELSE()
        MESSAGE(FATAL_ERROR "❌ Error: Found 32-bit Python. A 64-bit interpreter is required!")
    ENDIF()
ELSE()
    MESSAGE(FATAL_ERROR "❌ 找不到符合版本 (3.8 <= v < 3.14) 的 Python！")
ENDIF()

# =============================================================
# 虛擬環境(SETUP)
# =============================================================
SET(REQ_FILE "${CMAKE_SOURCE_DIR}/requirements.txt")

# 如果是 Release 模式，強制刪除 .venv 以確保環境絕對乾淨
# 使用 Cache 變數 (VENV_EXIST) 來判斷是否已經執行過清理
# 這樣可以避免每次修改 CMakeLists.txt (Reconfig) 時都觸發刪除
IF("${CMAKE_BUILD_TYPE}" STREQUAL "Release")
    # 只有當「.venv 存在」且「Cache 標記不存在」時才執行毀滅性清理
    IF(EXISTS "${VENV_DIR}" AND NOT VENV_EXIST)
        MESSAGE(STATUS "   [Mode: Release] Removing existing .venv for clean setup...")
        FILE(REMOVE_RECURSE "${VENV_DIR}")
        # 標記已清理，寫入 Cache (除非刪除 build 資料夾，否則此變數會一直存在)
        SET(VENV_EXIST TRUE CACHE INTERNAL "Venv exist for this build tree")
    ENDIF()
ENDIF()

# 建立/確保 venv 結構
MESSAGE(STATUS "Ensuring Python venv structure...")
EXECUTE_PROCESS(
    COMMAND "${Python3_EXECUTABLE}" -m venv "${VENV_DIR}"
    RESULT_VARIABLE VENV_RES
)
IF(NOT VENV_RES EQUAL 0)
    MESSAGE(FATAL_ERROR "Failed to create/update Python venv directory.")
ENDIF()

# pip 自行比對與更新
MESSAGE(STATUS "Updating Python venv dependencies from requirements.txt...")
EXECUTE_PROCESS(
    COMMAND "${VENV_PYTHON}" -m pip install -qq --upgrade pip
    RESULT_VARIABLE PIP_UPGRADE_RES
)
if(NOT PIP_UPGRADE_RES EQUAL 0)
    MESSAGE(FATAL_ERROR "Failed to upgrade pip. Aborting dependency installation.")
endif()

EXECUTE_PROCESS(
    # 這步切記要與upgrade pip分開寫
    COMMAND "${VENV_PYTHON}" -m pip install -qq -r "${REQ_FILE}"
    RESULT_VARIABLE PIP_RES
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)
IF(NOT PIP_RES EQUAL 0)
    MESSAGE(FATAL_ERROR "Python venv setup failed (pip install). Please check your connection or requirements.txt")
ENDIF()

MESSAGE(STATUS "✅ Python venv is ready.")

# =============================================================
# 檢查並打印重要套件版本 (CHECK PACKAGE VERSIONS)
# =============================================================
# 讀取 requirements.txt 的內容到變數 REQ_LINES (自動以換行分隔)
FILE(STRINGS "${REQ_FILE}" REQ_LINES)
MESSAGE(STATUS "📊 Checking installed library versions in venv (Target list from requirements.txt):")
SET(PKGS_TO_CHECK "")
# 迴圈處理每一行，過濾掉版本號、註解與空白
FOREACH(LINE ${REQ_LINES})
    # 去除前後空白
    STRING(STRIP "${LINE}" LINE)
    # 忽略空行 或 以 # 開頭的註解行
    IF(LINE STREQUAL "" OR LINE MATCHES "^#")
        CONTINUE()
    ENDIF()
    # 取出套件名稱：匹配字母、數字、底線、減號、點
    # 忽略後面的版本號 (例如 ==1.0, >=2.0, ;platform...)
    # 邏輯：把 "套件名" 之後遇到的第一個 =, <, >, ~, ; 及其後面所有內容都取代為空
    STRING(REGEX REPLACE "([a-zA-Z0-9_\\-\\.]+).*" "\\1" PURE_NAME "${LINE}")
    # 去除可能殘留的空白
    STRING(STRIP "${PURE_NAME}" PURE_NAME)
    # 加入清單
    LIST(APPEND PKGS_TO_CHECK "${PURE_NAME}")
ENDFOREACH()
# 執行檢查迴圈
FOREACH(PKG ${PKGS_TO_CHECK})
    EXECUTE_PROCESS(
        COMMAND "${VENV_PYTHON}" -c "from importlib.metadata import version; print(version('${PKG}'))"
        OUTPUT_VARIABLE PKG_VER
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    IF(PKG_VER)
        MESSAGE(STATUS "   📦 ${PKG}: ${PKG_VER}")
    ELSE()
        # 因為 requirements.txt 裡面的套件應該都要裝好，如果這裡沒裝到，顯示警告
        MESSAGE(STATUS "   ⚠️ ${PKG}: Not Found (Check installation)")
    ENDIF()
ENDFOREACH()

# =============================================================
# Python 打包
# =============================================================
ADD_CUSTOM_COMMAND(
    OUTPUT ${GEN_FW_PY}
    DEPENDS ${ATB_BIN} ${CONVERT_SCRIPT}
    COMMAND powershell -Command "Write-Host '>>> [generate_fw_py    Start] ' (Get-Date -Format 'HH:mm:ss')"
    COMMAND ${VENV_PYTHON} ${CONVERT_SCRIPT} ${ATB_BIN} ${GEN_FW_PY}
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Generating consolidated fw_bin.py from BIN files..."
)

ADD_CUSTOM_TARGET(generate_fw_py
    DEPENDS ${GEN_FW_PY}
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMAND powershell -Command "Write-Host '>>> [generate_fw_py Finished] ' (Get-Date -Format 'HH:mm:ss')"
    COMMENT "Manual trigger for firmware Python generation"
)

# =============================================================
# CSS 自動排版工具
# =============================================================
ADD_CUSTOM_TARGET(format_css
    DEPENDS generate_fw_py
    COMMAND powershell -Command "Write-Host '>>> [CSS Format Start] ' (Get-Date -Format 'HH:mm:ss')"
    COMMAND powershell -Command "& '${VENV_DIR}/Scripts/css-beautify.exe' -r '${CMAKE_SOURCE_DIR}/application/index.css'; exit 0"
    COMMAND powershell -Command "Write-Host '>>> [CSS Format Finished] ' (Get-Date -Format 'HH:mm:ss')"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Auto-formatting CSS files..."
)

# =============================================================
# 靜態型別檢查 (Static Type Checking)
# =============================================================
ADD_CUSTOM_TARGET(type_check
    DEPENDS format_css
    COMMAND powershell -Command "Write-Host '>>> [djlint Start] ' (Get-Date -Format 'HH:mm:ss')"
    # 掃描 application 內的所有 html 檔案
    # --extension html: 只看 HTML
    # --quiet: 減少冗餘輸出，只顯示錯誤
    # --ignore: 排除掉編譯產物或虛擬環境資料夾
    COMMAND ${VENV_PYTHON} -m djlint --extension html --ignore "H021,H030,H031,T001" --quiet --exclude "application/backend" "${CMAKE_SOURCE_DIR}/application "
    COMMAND powershell -Command "Write-Host '>>> [djlint Finished] ' (Get-Date -Format 'HH:mm:ss')"
    COMMAND powershell -Command "Write-Host '>>> [type_check:mypy    Start] ' (Get-Date -Format 'HH:mm:ss')"
    # 使用 mypy 掃描 application 資料夾, 忽略第三方套件警告, 並利用正則表達式排除 gens 子目錄
    COMMAND ${VENV_PYTHON} -m mypy "${CMAKE_SOURCE_DIR}/application/backend" --ignore-missing-imports --exclude "gens"
    COMMAND powershell -Command "Write-Host '>>> [type_check:mypy Finished] ' (Get-Date -Format 'HH:mm:ss')"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Running static type checker..."
)

ADD_CUSTOM_TARGET(package_nuitka
    DEPENDS type_check
    COMMAND powershell -Command "Write-Host '>>> [package_nuitka    Start] ' (Get-Date -Format 'HH:mm:ss')"
    # COMMAND ${CMAKE_COMMAND} -E env 
    #         PYTHONHASHSEED=0 
    #         # 讓編譯器能找到 backend 模組
    #         "PYTHONPATH=${CMAKE_SOURCE_DIR}/application;${CMAKE_SOURCE_DIR}/application/backend/src"
    #         "${VENV_PYTHON}" -m nuitka
    #         --standalone
    #         --jobs=8
    #         --mingw64
    #         --show-progress
    #         --assume-yes-for-downloads
    #         # --disable-console (除錯時先註解掉，可以看到 log)
    #         # 確保整個 backend 套件被編譯進去
    #         --include-package=backend
    #         # 手動包含所有網頁資源 ---
    #         # 主網頁檔案
    #         --include-data-files="${CMAKE_SOURCE_DIR}/application/index.html=index.html"
    #         # 前端資料夾 (來源=目標相對路徑)
    #         --include-data-dir="${CMAKE_SOURCE_DIR}/application=."
    #         --include-data-dir="${CMAKE_SOURCE_DIR}/application/blockly=blockly"
    #         --include-data-dir="${CMAKE_SOURCE_DIR}/application/mermaid=mermaid"
    #         --include-data-dir="${CMAKE_SOURCE_DIR}/application/script=script"
    #         --include-data-dir="${CMAKE_SOURCE_DIR}/application/backend/lib=backend/lib"
    #         --output-filename="${EXE_NAME}_nuitka"
    #         --windows-icon-from-ico="${APP_ICON}"
    #         --output-dir="${RELEASE_DIR}"
    #         --remove-output
    #         # 入口點路徑
    #         "${CMAKE_SOURCE_DIR}/application/index.py"
    COMMAND powershell -Command "Write-Host '>>> [package_nuitka Finished] ' (Get-Date -Format 'HH:mm:ss')"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Packaging Nuitka Standalone EXE with all frontend assets..."
)

ADD_CUSTOM_TARGET(package_exe
    DEPENDS package_nuitka
    COMMAND powershell -Command "Write-Host '>>> [package_exe    Start] ' (Get-Date -Format 'HH:mm:ss')"
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${RELEASE_DIR}/oneDir/_internal"
    COMMAND ${CMAKE_COMMAND} -E env PYTHONHASHSEED=0 "${VENV_PYTHON}" -m PyInstaller
                                    --clean
                                    --log-level FATAL
                                    -D
                                    -y
                                    --noconsole
                                    --name "${EXE_NAME}"
                                    --icon "${APP_ICON}"
                                    --paths ${CMAKE_SOURCE_DIR}/application/backend/lib
                                    --paths ${CMAKE_SOURCE_DIR}/application/backend/src
                                    --paths ${CMAKE_SOURCE_DIR}/application/backend/src/gens
                                    --paths ${CMAKE_SOURCE_DIR}/application/backend/src/resource
                                    --add-data "${RESOURCE_DIR}/index.html:."
                                    --add-data "${RESOURCE_DIR}/index.css:."
                                    --add-data "${RESOURCE_DIR}/blockly:blockly"
                                    --add-data "${RESOURCE_DIR}/media:media"
                                    --add-data "${RESOURCE_DIR}/mermaid:mermaid"
                                    --add-data "${RESOURCE_DIR}/script:script"
                                    --add-data "${CMAKE_SOURCE_DIR}/application/backend/lib:."
                                    --add-data "${CMAKE_SOURCE_DIR}/application/backend/src/DevVerifyGUI.ini:."
                                    --version-file "${GENERATED_VERSION_FILE}"
                                    --distpath "${CMAKE_BINARY_DIR}/temp_dist"
                                    --specpath "${CMAKE_BINARY_DIR}"
                                    --workpath "${CMAKE_BINARY_DIR}/pyinstaller_temp"
                                    "${PYTHON_SCRIPT}"
                                    --runtime-tmpdir=./tmp
    # COMMAND ${CMAKE_COMMAND} -E env PYTHONHASHSEED=0 "${VENV_PYTHON}" -m PyInstaller
    #                                 --clean
    #                                 --log-level FATAL
    #                                 -F
    #                                 -y
    #                                 # --noconsole
    #                                 --name "${EXE_NAME}"
    #                                 --icon "${APP_ICON}"
    #                                 --paths ${CMAKE_SOURCE_DIR}/application/backend/lib
    #                                 --paths ${CMAKE_SOURCE_DIR}/application/backend/src
    #                                 --paths ${CMAKE_SOURCE_DIR}/application/backend/src/gens
    #                                 --paths ${CMAKE_SOURCE_DIR}/application/backend/src/resource
    #                                 --add-data "${RESOURCE_DIR}/index.html:."
    #                                 --add-data "${RESOURCE_DIR}/index.css:."
    #                                 --add-data "${RESOURCE_DIR}/blockly:blockly"
    #                                 --add-data "${RESOURCE_DIR}/media:media"
    #                                 --add-data "${RESOURCE_DIR}/mermaid:mermaid"
    #                                 --add-data "${RESOURCE_DIR}/script:script"
    #                                 --add-data "${CMAKE_SOURCE_DIR}/application/backend/lib:."
    #                                 --add-data "${CMAKE_SOURCE_DIR}/application/backend/src/DevVerifyGUI.ini:."
    #                                 --version-file ${PY_EXE_DIR}/${EXE_NAME}.txt
    #                                 --distpath "${RELEASE_DIR}/oneFile"
    #                                 --specpath "${CMAKE_BINARY_DIR}"
    #                                 --workpath "${CMAKE_BINARY_DIR}/pyinstaller_temp"
    #                                 "${PYTHON_SCRIPT}"
    #                                 --runtime-tmpdir=./tmp
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_BINARY_DIR}/temp_dist/${EXE_NAME}" "${RELEASE_DIR}/oneDir"
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_BINARY_DIR}/temp_dist"
    COMMAND powershell -Command "Write-Host '>>> [package_exe Finished] ' (Get-Date -Format 'HH:mm:ss')"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Packaging Python EXE with Icon..."
)

# =============================================================
# 打包 VSIX (CONDITIONAL VSIX PACKAGING)
# =============================================================
IF(ENABLE_VSIX_PACKAGING)
    ADD_CUSTOM_TARGET(package_vsix
        DEPENDS package_exe
        COMMAND powershell -Command "Write-Host '>>> [package_vsix    Start] ' (Get-Date -Format 'HH:mm:ss')"
        COMMAND cmd /c "if not exist \"${RELEASE_DIR}\" mkdir \"${RELEASE_DIR}\""
        COMMAND "${CMAKE_COMMAND}" -E copy_directory "${RESOURCE_DIR}" "${VSCODE_EXT_DIR}/application"
        COMMAND npm ci --quiet --no-audit --no-fund
        COMMAND npx --no-install vsce package --allow-missing-repository --out "${RELEASE_DIR}/${EXE_NAME}.vsix"
        COMMAND "${NODE_EXECUTABLE}" -e "console.log('\\nPackaged Version: ' + require('./package.json').version + '\\n')"
        COMMAND powershell -Command "Write-Host '>>> [package_vsix Finished] ' (Get-Date -Format 'HH:mm:ss')"
        WORKING_DIRECTORY "${VSCODE_EXT_DIR}"
        COMMENT "Packaging VS Code Extension (${EXE_NAME}.vsix)..."
    )
    LIST(APPEND FINAL_DEPENDENCIES package_vsix)
ELSE()
    ADD_CUSTOM_TARGET(package_vsix
        DEPENDS package_exe
        COMMAND powershell -Command "Write-Host '>>> [package_vsix    Start] ' (Get-Date -Format 'HH:mm:ss')"
        COMMAND powershell -Command "Write-Host '>>> [package_vsix Finished] ' (Get-Date -Format 'HH:mm:ss')"
        WORKING_DIRECTORY "${VSCODE_EXT_DIR}"
        COMMENT "Ignore Packaging VS Code Extension (${EXE_NAME}.vsix)..."
    )
    LIST(APPEND FINAL_DEPENDENCIES package_vsix)
ENDIF()

# =============================================================
# 打包 ZIP (ZIP PACKAGING)
# =============================================================
# 使用 CMake 內建的 tar 功能來製作 zip 這樣不需要依賴 7-zip 也不會有 IT 權限問題
ADD_CUSTOM_TARGET(package_zip
    DEPENDS package_vsix
    COMMAND powershell -Command "Write-Host '>>> [package_zip    Start] ' (Get-Date -Format 'HH:mm:ss')"
    # 語法: cmake -E tar "cf" "輸出檔名.zip" --format=zip "要壓縮的資料夾"
    # COMMAND ${CMAKE_COMMAND} -E tar "cf" "${RELEASE_DIR}/${EXE_NAME}.zip" --format=zip "oneDir"
    # 將工作目錄設為 RELEASE_DIR/oneDir，這樣 ZIP 裡面的結構才會是 DevVerifyGUI/DevVerifyGUI.exe...
    COMMAND powershell -Command "Write-Host '>>> [package_zip Finished] ' (Get-Date -Format 'HH:mm:ss')"
    WORKING_DIRECTORY "${RELEASE_DIR}"
    COMMENT "Compressing ${EXE_NAME} folder into ${EXE_NAME}.zip..."
)

# =============================================================
# 自動觸發 CPack 打包 NSIS (AUTO TRIGGER CPACK)
# =============================================================
ADD_CUSTOM_TARGET(package_nsis
    DEPENDS package_zip
    COMMAND powershell -Command "Write-Host '>>> [package_nsis    Start] ' (Get-Date -Format 'HH:mm:ss')"
    # 在這邊 "偷渡" 要打包的檔案 (package_zip 的打包會不包含此檔案)
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${RELEASE_DIR}/fpga_autotest.hex"
            "${RELEASE_DIR}/oneDir/fpga_autotest.hex"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${RELEASE_DIR}/fpga_autotest_V30.hex"
            "${RELEASE_DIR}/oneDir/fpga_autotest_V30.hex"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${APP_README}
            "${RELEASE_DIR}/oneDir"
    # 呼叫 cpack 指令, --config CPackConfig.cmake 是指定 CMake 產生的設定檔
    # COMMAND cpack -G NSIS --config CPackConfig.cmake --no-preinstall  # Enable LOG for debugging
    COMMAND cmd /c "cpack -G NSIS --config CPackConfig.cmake --no-preinstall > NUL"
    # 打包完後，把檔案從 Build 資料夾搬到 Release 資料夾
    COMMAND ${CMAKE_COMMAND} -E rename 
            "${CMAKE_BINARY_DIR}/${EXE_NAME}_Setup.exe" 
            "${RELEASE_DIR}/${EXE_NAME}_Setup.exe"
    # CPack 必須在 build (Binary) 資料夾執行，因為 CPackConfig.cmake 在那裡
    # 在這邊移除 "偷渡" 的檔案
    COMMAND ${CMAKE_COMMAND} -E remove
            "${RELEASE_DIR}/oneDir/fpga_autotest.hex"
    COMMAND ${CMAKE_COMMAND} -E remove
            "${RELEASE_DIR}/oneDir/fpga_autotest_V30.hex"
    COMMAND ${CMAKE_COMMAND} -E remove
            "${RELEASE_DIR}/oneDir/README.md"
    COMMAND powershell -Command "Write-Host '>>> [package_nsis Finished] ' (Get-Date -Format 'HH:mm:ss')"
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    COMMENT "Running CPack (NSIS) and moving installer to Release folder... (Quiet Mode)"
)

# 將 ZIP & NSIS 打包加入最終依賴清單
LIST(APPEND FINAL_DEPENDENCIES package_nsis)

# =============================================================
# 總任務 (PACKAGE ALL)
# =============================================================
ADD_CUSTOM_TARGET(package_all ALL
    DEPENDS ${FINAL_DEPENDENCIES}
    COMMAND powershell -Command "Write-Host '>>> [package_all    Start] ' (Get-Date -Format 'HH:mm:ss')"
    COMMAND ${VENV_PYTHON} "${CMAKE_SOURCE_DIR}/tools/cleanup.py"
    COMMAND powershell -Command "Write-Host '>>> [package_all Finished] ' (Get-Date -Format 'HH:mm:ss')"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Build Process Completed! Artifacts (EXE folder & ZIP) are in ${RELEASE_DIR}"
)

SET(CPACK_INSTALL_CMAKE_PROJECTS "")
# 啟用 CPack (這行必須放在最後)
INCLUDE(CPack)
