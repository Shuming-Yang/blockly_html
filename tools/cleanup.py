import time
import os
import shutil
import stat

# 定義要清理的資料夾清單
FOLDERS_TO_CLEAN = [
    "vscode_ext/application", 
    "vscode_ext/node_modules",
    "application/__pycache__",
    "application/backend/src/__pycache__",
    "application/backend/src/gens/__pycache__",
    "application/backend/src/resource/__pycache__",
    # ".venv", # 開發階段也都會使用.venv，因此不在這邊清除，透過release時重建確保環境乾淨
]

def remove_readonly(func, path, _):
    """強力刪除：遇到唯讀檔案時，強制更改權限後再刪除"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main():
    # print("[CleanUp] Waiting 10 seconds for file locks to release...")
    time.sleep(10)

    for folder in FOLDERS_TO_CLEAN:
        if os.path.exists(folder):
            time.sleep(2)
            try:
                print(f"[CleanUp] Removing: {folder}")
                # shutil.rmtree 是 Python 的強力刪除
                # onexc=remove_readonly 可以解決 Windows 上常遇到的「存取被拒」問題
                shutil.rmtree(folder, onexc=remove_readonly)
            except Exception as e:
                print(f"[CleanUp] Failed to remove {folder} {e}")
        else:
            print(f"[CleanUp] {folder} already gone.")
    print("[CleanUp] Done!")

if __name__ == "__main__":
    main()
