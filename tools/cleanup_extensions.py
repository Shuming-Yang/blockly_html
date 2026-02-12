import subprocess
import json
import re

# 這"允許清單" (白名單) 是由extension.json 內容提取出來 (轉為全小寫以防大小寫誤差)
ALLOWED_EXTENSIONS = {
    "ms-python.python", "ms-python.pylint", "ms-python.vscode-pylance",
    "ms-python.debugpy", "ms-python.autopep8", "ms-python.vscode-python-envs",
    "donjayamanne.python-environment-manager", "kevinrose.vsc-python-indent",
    "njpwerner.autodocstring", "nikolapaunovic.tkinter-snippets",
    "dbaeumer.vscode-eslint",
    "ms-vscode.cpptools-extension-pack", "ms-vscode.cpptools",
    "ms-vscode.cpptools-themes", "llvm-vs-code-extensions.vscode-clangd",
    "vadimcn.vscode-lldb", "sumfish.cpp-checker-misra",
    "mcu-debug.debug-tracker-vscode", "mcu-debug.memory-view",
    "ms-vscode.vscode-serial-monitor", "ms-vscode.hexeditor",
    "ms-vscode.makefile-tools", "ms-vscode.cmake-tools", "twxs.cmake",
    "josetr.cmake-language-support-vscode", "zchrissirhcz.cmake-highlight",
    "yzhang.markdown-all-in-one", "bierner.markdown-mermaid",
    "bpruitt-goddard.mermaid-markdown-syntax-highlighting",
    "shd101wyy.markdown-preview-enhanced", "charleswan.markdown-toc",
    "marp-team.marp-vscode", "zcs.md-ppt", "goessner.mdmath",
    "koehlma.markdown-math", "james-yu.latex-workshop",
    "chrischinchilla.vscode-pandoc", "cschlosser.doxdocgen",
    "analytic-signal.preview-pdf", "deadpoulpe.custom-md-pdf",
    "bierner.markdown-emoji", "bierner.markdown-preview-github-styles",
    "darkriszty.markdown-table-prettify", "zaaack.markdown-editor",
    "ms-vscode-remote.vscode-remote-extensionpack", "ms-vscode-remote.remote-ssh",
    "ms-vscode-remote.remote-ssh-edit", "ms-vscode-remote.remote-wsl",
    "ms-vscode-remote.remote-containers", "ms-vscode-remote.remote-server",
    "ms-vscode.remote-explorer", "kelvin.vscode-sshfs",
    "alefragnani.project-manager", "zhucy.project-tree", "mhutchie.git-graph",
    "donjayamanne.githistory", "gruntfuggly.todo-tree",
    "google.geminicodeassist", "google.gemini-cli-vscode-ide-companion",
    "ms-ceintl.vscode-language-pack-zh-hant",
    "aaron-bond.better-comments", "pkief.material-icon-theme",
    "mechatroner.rainbow-csv", "grapecity.gc-excelviewer",
    "mindaro-dev.file-downloader", "redhat.vscode-xml", "zainchen.json",
    "imgildev.vscode-json-flow",
    "nickdemayo.vscode-json-editor", "ibm.output-colorizer",
    "oderwat.indent-rainbow", "qrti.funclist", "flyfly6.terminal-in-status-bar",
    "ms-dotnettools.vscode-dotnet-runtime", "ms-edgedevtools.vscode-edge-devtools",
    "ms-vscode.extension-test-runner", "fougas.msys2",
    "kruemelkatze.vscode-dashboard"
}

# 將白名單轉為小寫集合，方便比對
allowed_set = {x.lower() for x in ALLOWED_EXTENSIONS}

def get_installed_extensions():
    print("正在讀取 VS Code 已安裝列表...")
    try:
        # 使用 utf-8 解碼輸出，避免中文環境下的亂碼問題
        result = subprocess.check_output(["code", "--list-extensions"], shell=True)
        installed_list = result.decode("utf-8").splitlines()
        return [ext.strip().lower() for ext in installed_list if ext.strip()]
    except subprocess.CalledProcessError:
        print("錯誤：無法執行 'code' 指令。請確認 VS Code 的 bin 目錄是否在環境變數 PATH 中。")
        return []

def main():
    installed = get_installed_extensions()
    if not installed:
        return
    to_remove = []
    print(f"\n目前共安裝了 {len(installed)} 個套件。")
    print("-" * 40)
    for ext in installed:
        if ext not in allowed_set:
            to_remove.append(ext)
    if not to_remove:
        print("完美！你的環境非常乾淨，沒有多餘的套件。")
    else:
        print(f"發現 {len(to_remove)} 個不在白名單內的套件：\n")
        uninstall_cmd_filename = "uninstall_extras.bat"
        with open(uninstall_cmd_filename, "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("echo Start uninstalling extensions...\n")
            for ext in to_remove:
                print(f"  [X] {ext}")
                # 寫入移除指令
                f.write(f"call code --uninstall-extension {ext} --force\n")
            f.write("echo Done!\n")
            f.write("pause\n")
        print("-" * 40)
        print(f"已生成移除腳本： {uninstall_cmd_filename}")
        print("請檢查上述列表，確認無誤後，執行該 bat 檔即可一次移除所有多餘套件。")

if __name__ == "__main__":
    main()
