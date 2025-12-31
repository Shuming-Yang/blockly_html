import time
import os
import shutil
import stat

# 定義要清理的資料夾清單
FOLDERS_TO_CLEAN = [
    "venv",
    "vscode_ext/application", 
    "vscode_ext/node_modules"
]

def remove_readonly(func, path, _):
    """強力刪除：遇到唯讀檔案時，強制更改權限後再刪除"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main():
    # print("[CleanUp] Waiting 20 seconds for file locks to release...")
    # 這就是我們要的延遲，不管在哪個環境都有效
    time.sleep(20) 

    for folder in FOLDERS_TO_CLEAN:
        if os.path.exists(folder):
            time.sleep(2)
            try:
                print(f"[CleanUp] Removing: {folder}")
                # shutil.rmtree 是 Python 的強力刪除
                # onexc=remove_readonly 可以解決 Windows 上常遇到的「存取被拒」問題
                shutil.rmtree(folder, onexc=remove_readonly)
            except Exception as e:
                print(f"[CleanUp] Failed to remove {folder}")
        else:
            print(f"[CleanUp] {folder} already gone.")

    print("[CleanUp] Done!")

if __name__ == "__main__":
    main()