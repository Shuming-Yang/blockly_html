const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

// 1. 全域變數：用來記住目前開啟的面板 (單例模式)
/** @type {vscode.WebviewPanel | undefined} */
let currentPanel = undefined;

function activate(context) {
    // -------------------------------------------------------------------------
    // 主指令：開啟儀表板
    // -------------------------------------------------------------------------
    let disposable = vscode.commands.registerCommand('helloworld.helloWorld', function () {
        const columnToShowIn = vscode.ViewColumn.One;

        // =====================================================================
        // ★ 核心修改：智慧路徑偵測 (解決 F5 開發與打包後的路徑差異)
        // =====================================================================
        let htmlPath = null;
        
        // 1. 先找「正式環境」路徑 (安裝後，application 會被複製到 extension 資料夾內)
        const productionPath = path.join(context.extensionPath, 'application', 'index.html');
        
        // 2. 再找「開發環境」路徑 (F5 debug 時，application 在上一層)
        const developmentPath = path.join(context.extensionPath, '..', 'application', 'index.html');

        if (fs.existsSync(productionPath)) {
            htmlPath = productionPath;
            console.log('✅ 使用正式環境路徑:', htmlPath);
        } else if (fs.existsSync(developmentPath)) {
            htmlPath = developmentPath;
            console.log('🔧 使用開發環境路徑:', htmlPath);
        } else {
            vscode.window.showErrorMessage('❌ 嚴重錯誤：找不到 application/index.html！');
            return;
        }
        // =====================================================================

        if (currentPanel) {
            // 2. 焦點修復 (Part A)：
            currentPanel.reveal(columnToShowIn, false);
        } else {
            // 建立新的面板
            currentPanel = vscode.window.createWebviewPanel(
                'helloWorldView',
                '專案儀表板',
                columnToShowIn,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true,
                    // ★ 權限設定：允許 Webview 讀取 application 資料夾 與 media 資料夾
                    localResourceRoots: [
                        vscode.Uri.file(path.dirname(htmlPath)), 
                        vscode.Uri.file(path.join(context.extensionPath, 'media'))
                    ]
                }
            );

            // 讀取並載入 HTML
            const htmlContent = fs.readFileSync(htmlPath, 'utf8');
            currentPanel.webview.html = htmlContent;

            // 監聽關閉事件，清理變數
            currentPanel.onDidDispose(
                () => {
                    currentPanel = undefined;
                },
                null,
                context.subscriptions
            );
        }
    });
    context.subscriptions.push(disposable);


    // -------------------------------------------------------------------------
    // 側邊欄觸發器 (自動跳轉邏輯)
    // -------------------------------------------------------------------------
    const provider = new SidebarProvider(context.extensionUri);
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('my-extension-view', provider)
    );
}


// -------------------------------------------------------------------------
// 側邊欄類別 (SidebarProvider)
// -------------------------------------------------------------------------
class SidebarProvider {
    constructor(extensionUri) {
        this._extensionUri = extensionUri;
    }

    resolveWebviewView(webviewView) {
        webviewView.webview.options = { enableScripts: true };

        // 設定 HTML (含手動按鈕，以防萬一)
        webviewView.webview.html = `
            <html>
            <body style="display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
                <div style="text-align:center;">
                    <h3>🚀 正在啟動...</h3>
                    <p style="font-size:12px; color:#888;">如果沒有自動開啟，請點擊下方按鈕</p>
                    <button id="manual-btn" style="padding:8px 16px; cursor:pointer;">手動啟動</button>
                </div>
                <script>
                    const vscode = acquireVsCodeApi();
                    document.getElementById('manual-btn').addEventListener('click', () => {
                        vscode.postMessage({ command: 'openDashboard' });
                    });
                </script>
            </body>
            </html>
        `;

        // 監聽手動按鈕訊息
        webviewView.webview.onDidReceiveMessage(data => {
            if (data.command === 'openDashboard') {
                this._openAndSwitch(webviewView);
            }
        });

        // 定義自動啟動函式
        const tryToAutoLaunch = () => {
            if (webviewView.visible) {
                this._openAndSwitch(webviewView);
            }
        };

        // 3. 第一次啟動修復：
        setTimeout(tryToAutoLaunch, 300);

        // 4. 第二次以後啟動：
        webviewView.onDidChangeVisibility(tryToAutoLaunch);
    }

    // 抽取出共用的開啟與跳轉邏輯
    _openAndSwitch(webviewView) {
        const vscode = require('vscode'); 

        // 動作 A: 執行開啟 Dashboard
        vscode.commands.executeCommand('helloworld.helloWorld');

        // 動作 B: 延遲跳轉
        setTimeout(() => {
            // 先切換回檔案總管
            vscode.commands.executeCommand('workbench.view.explorer').then(() => {
                
                // 5. 焦點修復 (Part B)：
                vscode.commands.executeCommand('workbench.action.focusActiveEditorGroup');
                
            });
        }, 200); 
    }
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
}
