const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

/**
 * 取得 VS Code 當前選用的 Python 解譯器路徑
 */
// eslint-disable-next-line no-unused-vars
function getVSCodePythonPath(context) {
    // 1. 讀取 Python 擴充套件的設定
    const config = vscode.workspace.getConfiguration('python');
    let pythonPath = config.get('defaultInterpreterPath');
    // 2. 如果設定不存在，預設回傳 'python' (系統預設)
    if (!pythonPath) {
        return 'python';
    }
    // 3. 處理 ${workspaceFolder} 變數
    // 因為 VS Code 的路徑設定有時會寫成 "${workspaceFolder}/.venv/..."
    if (pythonPath.includes('${workspaceFolder}')) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            // 將變數替換為實際的路徑
            pythonPath = pythonPath.replace('${workspaceFolder}', workspaceFolders[0].uri.fsPath);
        } else {
            // 如果沒有開啟任何資料夾，這路徑可能無效，退回系統預設
            return 'python';
        }
    }
    // 4. 處理相對路徑 (例如 "./.venv/...") - 將其轉為絕對路徑
    if (pythonPath.startsWith('./') || pythonPath.startsWith('.\\')) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            pythonPath = path.resolve(workspaceFolders[0].uri.fsPath, pythonPath);
        }
    }
    return pythonPath;
}

/**
 * 檢查指定的 Python 環境是否已安裝該模組
 * 原理：執行 python -c "import xxx"，如果 exit code 為 0 代表存在
 */
function isPackageInstalled(pythonPath, moduleName) {
    try {
        // 使用 execSync 進行快速檢查
        cp.execSync(`"${pythonPath}" -c "import ${moduleName}"`, { encoding: 'utf8' });
        return true;
    // eslint-disable-next-line no-unused-vars
    } catch (error) {
        return false;
    }
}

/**
 * 跳出進度條並執行 pip install
 */
async function installPackage(pythonPath, packageName) {
    return vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `installing ${packageName}...`,
        cancellable: false
    // eslint-disable-next-line no-unused-vars
    }, async (progress) => {
        // eslint-disable-next-line no-unused-vars
        return new Promise((resolve, reject) => {
            // 使用 -m pip 可以確保安裝到對應的 Python 環境
            const installProcess = cp.spawn(pythonPath, [
                '-m', 'pip', 'install', packageName, '--user'
            ]);
            // 監聽輸出
            installProcess.stdout.on('data', (data) => {
                console.log(`[Install]: ${data}`);
            });
            installProcess.on('close', (code) => {
                if (code === 0) {
                    vscode.window.showInformationMessage(`✅ ${packageName} installed successfully.`);
                    resolve(true);
                } else {
                    vscode.window.showErrorMessage(`❌ ${packageName} install Failed. Code: ${code}`);
                    resolve(false);
                }
            });
        });
    });
}

// Create a dedicated output channel for debugging
const outputChannel = vscode.window.createOutputChannel("DevVerifyGUI Python Log");

/** @type {cp.ChildProcessWithoutNullStreams | null} */
let pythonProcess = null; // Store the Python process

function activate(context) {
    // -------------------------------------------------------------------------
    // Main Command: Launch Standalone Python App
    // -------------------------------------------------------------------------
    let disposable = vscode.commands.registerCommand('helloworld.helloWorld', async function () {
        // Prevent multiple instances
        if (pythonProcess && !pythonProcess.killed) {
            vscode.window.showWarningMessage("⚠️ Application is already running! Please check your taskbar.");
            return;
        }
        // 加上 await，等待啟動完成 (包含可能的安裝過程)
        await launchPythonStandalone(context);
    });
    context.subscriptions.push(disposable);
    // -------------------------------------------------------------------------
    // Sidebar View - Launch Button
    // -------------------------------------------------------------------------
    const provider = new SidebarProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('my-extension-view', provider)
    );
}

/**
 * Core Function: Launch Python and spawn a standalone window
 */
async function launchPythonStandalone(context) {
    outputChannel.show(true); // Bring output window to focus
    outputChannel.appendLine("🚀 Launching standalone application...");
    // =====================================================================
    // 獲取 VS Code 當前選用的 Python
    // =====================================================================
    let pythonPath = getVSCodePythonPath(context);
    outputChannel.appendLine(`🐍 Target Python Interpreter: ${pythonPath}`);
    // 如果抓到的是相對路徑或只有 "python"，檢查一下實際執行位置
    if (pythonPath === 'python') {
        outputChannel.appendLine("ℹ️ Using system global python command.");
    }
    // =====================================================================
    // 「檢查並安裝套件」的邏輯
    // =====================================================================
    const requiredImport = "webview"; 
    const pipPackage = "pywebview";   
    if (!isPackageInstalled(pythonPath, requiredImport)) {
        outputChannel.appendLine(`⚠️ Module '${requiredImport}' not found.`);
        // Show warning message asking for installation
        const selection = await vscode.window.showWarningMessage(
            `The required package '${pipPackage}' is missing from your Python environment. Would you like to install it now?`,
            "Yes, install now", 
            "Cancel"
        );
        // 這裡的判斷字串必須跟上面的按鈕文字完全一樣
        if (selection === "Yes, install now") {
            const success = await installPackage(pythonPath, pipPackage);
            if (!success) {
                outputChannel.appendLine("❌ Installation failed. Aborting launch.");
                return; // Installation failed
            }
            outputChannel.appendLine("✅ Installation completed. Continuing launch...");
        } else {
            outputChannel.appendLine("❌ User cancelled installation. Aborting launch.");
            return; // User cancelled
        }
    }
    // =====================================================================
    // Locate Python Script (index.py)
    // =====================================================================
    let scriptPath = "";
    const prodScript = path.join(context.extensionPath, 'application', 'index.py');
    const devScript = path.join(context.extensionPath, '..', 'application', 'index.py');
    if (fs.existsSync(prodScript)) {
        scriptPath = prodScript;
    } else if (fs.existsSync(devScript)) {
        scriptPath = devScript;
        outputChannel.appendLine("📂 Mode: Development Environment (Source)");
    } else {
        vscode.window.showErrorMessage("❌ Critical Error: index.py not found!");
        outputChannel.appendLine("❌ Critical Error: index.py not found at expected paths.");
        return;
    }
    // =====================================================================
    // Spawn Process
    // =====================================================================
    const scriptDir = path.dirname(scriptPath);
    // 判斷是否為開發模式 (用來決定是否開啟 debugpy 等待)
    const isDevMode = context.extensionMode === vscode.ExtensionMode.Development;
    pythonProcess = cp.spawn(pythonPath, [
        '-Xfrozen_modules=off',
        '-u',
        scriptPath
    ], {
        cwd: scriptDir,
        env: { 
            ...process.env,
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "VSCODE_LAUNCHED": "true",
            "SHOW_GUI": "true",
            // 如果是開發模式才開啟 Debug 等待
            "ENABLE_DEBUGPY": isDevMode ? "true" : "false" 
        } 
    });
    outputChannel.appendLine(`⚡ Process started. PID: ${pythonProcess.pid}`);
    vscode.window.showInformationMessage("✅ Application launching, please check your taskbar...");
    // Pipe Logs (Python stdout -> VS Code Output)
    pythonProcess.stdout.on('data', (data) => {
        outputChannel.appendLine(`[App]: ${data.toString().trim()}`);
    });
    pythonProcess.stderr.on('data', (data) => {
        outputChannel.appendLine(`[Error]: ${data.toString().trim()}`);
    });
    pythonProcess.on('close', (code) => {
        outputChannel.appendLine(`💀 Application exited (Code: ${code})`);
        pythonProcess = null;
    });
}

// -------------------------------------------------------------------------
// Sidebar Class (Launch Button UI)
// -------------------------------------------------------------------------
class SidebarProvider {
    constructor(extensionUri) {
        this._extensionUri = extensionUri;
    }
    resolveWebviewView(webviewView) {
        webviewView.webview.options = { enableScripts: true };
        webviewView.webview.html = `
            <html>
            <body style="display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif; background-color:var(--vscode-editor-background); color:var(--vscode-editor-foreground);">
                <div style="text-align:center;">
                    <h3>🚀 DevVerify GUI</h3>
                    <p style="font-size:12px; opacity:0.8; margin-bottom: 20px;">Click the button below to launch the standalone window.</p>
                    <button id="launch-btn" style="
                        padding: 10px 20px; 
                        background-color: var(--vscode-button-background); 
                        color: var(--vscode-button-foreground); 
                        border: none; 
                        cursor: pointer;
                        font-size: 14px;
                        border-radius: 2px;">
                        Launch Application
                    </button>
                </div>
                <script>
                    const vscode = acquireVsCodeApi();
                    document.getElementById('launch-btn').addEventListener('click', () => {
                        vscode.postMessage({ command: 'startApp' });
                    });
                </script>
            </body>
            </html>
        `;

        webviewView.webview.onDidReceiveMessage(data => {
            if (data.command === 'startApp') {
                vscode.commands.executeCommand('helloworld.helloWorld');
            }
        });
    }
}

function deactivate() {
    if (pythonProcess) {
        pythonProcess.kill();
    }
}

module.exports = { activate, deactivate }