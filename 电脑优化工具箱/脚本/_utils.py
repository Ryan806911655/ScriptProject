"""
共享工具模块 — 控制台颜色、管理员检测、系统工具函数
"""

import ctypes
import os
import sys
import subprocess
import shutil
import unicodedata

# ---------- 控制台颜色 ----------
COLORS = {
    "black": 0, "blue": 1, "green": 2, "cyan": 3,
    "red": 4, "magenta": 5, "yellow": 6, "white": 7,
    "gray": 8, "lblue": 9, "lgreen": 10, "lcyan": 11,
    "lred": 12, "lmagenta": 13, "lyellow": 14, "lwhite": 15,
}

_kernel32 = ctypes.windll.kernel32

def set_color(color="white"):
    code = COLORS.get(color, 7)
    _kernel32.SetConsoleTextAttribute(_kernel32.GetStdHandle(-11), code)

def cprint(text, color="white", end="\n"):
    """打印彩色文字"""
    set_color(color)
    print(text, end=end)
    set_color("white")

def ok(text):   cprint(f"  [OK] {text}", "lgreen")
def info(text): cprint(f"  [i] {text}", "lcyan")
def warn(text): cprint(f"  [!] {text}", "lyellow")
def err(text):  cprint(f"  [X] {text}", "lred")

# ---------- 管理员权限 ----------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    """以管理员权限重新启动当前脚本"""
    script = os.path.abspath(sys.argv[0])
    params = f'"{script}"'
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    return result > 32

def require_admin():
    """检查管理员权限，没有则自动提权后退出"""
    if not is_admin():
        warn("需要管理员权限，正在自动提权...")
        if relaunch_as_admin():
            info("请在弹出的 UAC 窗口中点击「是」")
            sys.exit(0)
        else:
            err("提权失败！请右键「以管理员身份运行」")
            input("\n  按回车退出...")
            sys.exit(1)

# ---------- 系统工具 ----------
def run_cmd(cmd, capture=True):
    """执行命令"""
    if capture:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           encoding="gbk", errors="replace")
        return r.stdout.strip()
    else:
        subprocess.run(cmd, shell=True)
        return ""

def get_disk_space(path):
    """获取磁盘空间 (GB)"""
    try:
        total, used, free = shutil.disk_usage(path)
        return total / (1024**3), used / (1024**3), free / (1024**3)
    except Exception:
        return 0, 0, 0

def format_bytes(b):
    """格式化字节"""
    for u in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} PB"

def get_dir_size(path):
    """计算目录大小"""
    total = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total

def safe_delete(path):
    """安全删除文件/文件夹"""
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
            return True
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            return True
    except (OSError, PermissionError):
        pass
    return False

def safe_clean_dir(path):
    """清空目录内容（保留目录本身）"""
    if not os.path.isdir(path):
        return 0
    count = 0
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                count += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)
                count += 1
        except (OSError, PermissionError):
            pass
    return count

def pause():
    print()
    input("  按回车继续...")

# ---------- 显示宽度（中英文混排对齐） ----------
def display_width(s):
    """计算字符串在终端中的显示宽度（CJK=2, ASCII=1）"""
    w = 0
    for c in str(s):
        w += 2 if unicodedata.east_asian_width(c) in ('F', 'W') else 1
    return w

def pad_display(s, target_width):
    """将字符串补齐到目标显示宽度（右侧补空格）"""
    current = display_width(s)
    return s + ' ' * (target_width - current)

SEP  = "=" * 56
SEP2 = "-" * 56
