CMAKE_MINIMUM_REQUIRED(VERSION 3.10)
PROJECT(HelloWorldExtension)

# =============================================================
# 1. 環境檢測與相依性安裝 (DEPENDENCY CHECK & INSTALL)
# =============================================================

# (A) 尋找 Node.js
FIND_PROGRAM(NODE_EXECUTABLE NAMES node node.exe)
# 預設不開啟 VSIX 打包，直到通過層層檢查
SET(ENABLE_VSIX_PACKAGING FALSE)
IF(NODE_EXECUTABLE)
    MESSAGE(STATUS "✅ Found Node.js: ${NODE_EXECUTABLE}")
    # (B) 尋找 NPM
    IF(WIN32)
        FIND_PROGRAM(NPM_EXECUTABLE NAMES npm.cmd npm)
    ELSE()
        FIND_PROGRAM(NPM_EXECUTABLE NAMES npm)
    ENDIF()
    IF(NPM_EXECUTABLE)
        MESSAGE(STATUS "✅ Found NPM: ${NPM_EXECUTABLE}")
        # (C) 尋找 VSCE
        IF(WIN32)
            FIND_PROGRAM(VSCE_EXECUTABLE NAMES vsce.cmd vsce)
        ELSE()
            FIND_PROGRAM(VSCE_EXECUTABLE NAMES vsce)
        ENDIF()
        # 如果找不到 vsce，嘗試自動安裝
        IF(NOT VSCE_EXECUTABLE)
            MESSAGE(STATUS "⚠️  'vsce' not found. Attempting to install via npm...")
            EXECUTE_PROCESS(COMMAND "${NPM_EXECUTABLE}" install -g @vscode/vsce RESULT_VARIABLE INSTALL_RESULT)
            IF("${INSTALL_RESULT}" STREQUAL "0")
                MESSAGE(STATUS "✅ 'vsce' installed successfully!")
                SET(ENABLE_VSIX_PACKAGING TRUE)
            ELSE()
                MESSAGE(WARNING "❌ Failed to install 'vsce'. VSIX packaging will be skipped.")
            ENDIF()
        ELSE()
            MESSAGE(STATUS "✅ Found VSCE: ${VSCE_EXECUTABLE}")
            SET(ENABLE_VSIX_PACKAGING TRUE)
        ENDIF()
    ELSE()
        MESSAGE(WARNING "⚠️  Node.js found but NPM not found. Cannot check/install vsce.")
    ENDIF()
ELSE()
    MESSAGE(STATUS "⚠️  Node.js NOT found. VSIX packaging will be SKIPPED.")
ENDIF()


# =============================================================
# 2. 設定變數 (VARIABLES)
# =============================================================
SET(EXE_NAME "DevVerifyGUI")
# 路徑設定
SET(RESOURCE_DIR "${CMAKE_SOURCE_DIR}/application")
# 指向 application 資料夾內的 index.py
SET(PYTHON_SCRIPT "${RESOURCE_DIR}/index.py") 
SET(RELEASE_DIR "${CMAKE_SOURCE_DIR}/release")
SET(VSCODE_EXT_DIR "${CMAKE_SOURCE_DIR}/vscode_ext")
SET(APP_ICON "${CMAKE_SOURCE_DIR}/py_exe/icon.ico")
# 虛擬環境路徑
SET(VENV_DIR "${CMAKE_SOURCE_DIR}/venv")
SET(VENV_PYTHON "${VENV_DIR}/Scripts/python.exe")
SET(VENV_PIP "${VENV_DIR}/Scripts/pip.exe")
SET(VENV_PYINSTALLER "${VENV_DIR}/Scripts/pyinstaller.exe")
# 建立最終任務清單 (Python EXE 是必備的)
SET(FINAL_DEPENDENCIES package_exe)

# =============================================================
# 3. 虛擬環境與 Python 打包 (SETUP & PACKAGE EXE)
# =============================================================
ADD_CUSTOM_TARGET(setup_venv
    COMMAND py -3.12 -m venv "${VENV_DIR}"
    COMMAND "${VENV_PIP}" install pywebview pyinstaller
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Setting up clean Python Virtual Environment (venv)..."
)

ADD_CUSTOM_TARGET(package_exe
    DEPENDS setup_venv
    COMMAND "${VENV_PYINSTALLER}"   --log-level ERROR
                                    --noconsole
                                    --onefile
                                    --name "${EXE_NAME}"
                                    --icon "${APP_ICON}"
                                    --add-data "${RESOURCE_DIR};."
                                    --exclude-module tkinter
                                    --distpath "${RELEASE_DIR}"
                                    --specpath "${CMAKE_BINARY_DIR}"
                                    --workpath "${CMAKE_BINARY_DIR}/pyinstaller_temp"
                                    "${PYTHON_SCRIPT}"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Packaging Python EXE with Icon..."
)

# =============================================================
# 4. 條件式：打包 VSIX (CONDITIONAL VSIX PACKAGING)
# =============================================================
IF(ENABLE_VSIX_PACKAGING)
    ADD_CUSTOM_TARGET(package_vsix
        DEPENDS package_exe
        # 1. 確保輸出目錄存在
        COMMAND cmd /c "if not exist \"${RELEASE_DIR}\" mkdir \"${RELEASE_DIR}\""
        # 2. 複製資源：把 application 複製到 vscode_ext 裡面
        # 這是因為 vsce 只能打包當前目錄下的檔案
        COMMAND "${CMAKE_COMMAND}" -E copy_directory "${RESOURCE_DIR}" "${VSCODE_EXT_DIR}/application"
        # 3. 安裝依賴 (使用 npm ci 進行乾淨安裝，需 package-lock.json)
        COMMAND npm ci
        # 4. 執行打包 (輸出到 release 目錄)
        COMMAND npx --no-install vsce package --out "${RELEASE_DIR}/extension.vsix"
        # 5. 打印版本號 (讀取 package.json)
        COMMAND "${NODE_EXECUTABLE}" -e "console.log('\\nPackaged Version: ' + require('./package.json').version + '\\n')"
        # ★ 設定工作目錄在 vscode_ext 裡面
        WORKING_DIRECTORY "${VSCODE_EXT_DIR}"
        COMMENT "Packaging VS Code Extension (.vsix)..."
    )
    # 將 package_vsix 加入最終任務清單
    LIST(APPEND FINAL_DEPENDENCIES package_vsix)
ENDIF()


# =============================================================
# 5. 總任務 (PACKAGE ALL)
# =============================================================
ADD_CUSTOM_TARGET(package_all ALL
    DEPENDS ${FINAL_DEPENDENCIES}
    # 呼叫外部腳本進行清理
    COMMAND python "${CMAKE_SOURCE_DIR}/cleanup.py"
    COMMENT "Build Process Completed! Cleanup script executed. Artifacts are in ${RELEASE_DIR}"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)