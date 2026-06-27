"""
系统信息检测 — 查看硬件配置、系统版本、激活状态，支持导出报告
"""

import os
import sys
import socket
import platform
import datetime
import winreg
from _utils import *


def get_os_info():
    """操作系统信息"""
    cprint("  [ 操作系统 ]", "lyellow")
    print(f"  系统版本：{platform.system()} {platform.release()}")
    print(f"  架构：    {platform.architecture()[0]}  |  计算机名：{socket.gethostname()}")
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
            name, _ = winreg.QueryValueEx(key, "ProductName")
            build, _ = winreg.QueryValueEx(key, "CurrentBuild")
            print(f"  产品名称：{name}")
            print(f"  内部版本：{build}")
    except Exception:
        pass


def get_cpu_info():
    """CPU 信息"""
    print()
    cprint("  [ 处理器 CPU ]", "lyellow")
    try:
        r = run_cmd("wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors /format:csv")
        if r:
            lines = r.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split(",")
                print(f"  型号：{parts[-1].strip()}")
                if len(parts) >= 3:
                    print(f"  物理核心：{parts[1].strip()}  |  逻辑核心：{parts[2].strip()}")
    except Exception:
        pass
    print(f"  系统识别核心数：{os.cpu_count()}")


def get_memory_info():
    """内存信息"""
    print()
    cprint("  [ 内存 RAM ]", "lyellow")
    try:
        r = run_cmd("wmic ComputerSystem get TotalPhysicalMemory /format:csv")
        if r:
            lines = r.strip().split("\n")
            if len(lines) >= 2:
                total = int(lines[1].split(",")[-1].strip())
                print(f"  总内存：{format_bytes(total)}")
    except Exception:
        pass

    # 当前使用情况（用 psutil 或 wmic）
    try:
        r = run_cmd("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /format:csv")
        if r:
            lines = r.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split(",")
                if len(parts) >= 3:
                    free = int(parts[-2].strip()) * 1024
                    total = int(parts[-1].strip()) * 1024
                    used = total - free
                    pct = (used / total) * 100
                    print(f"  已用：{format_bytes(used)} / {format_bytes(total)} ({pct:.0f}%)")
    except Exception:
        pass


def get_disk_info():
    """磁盘信息（带进度条）"""
    print()
    cprint("  [ 磁盘空间 ]", "lyellow")
    drives_info = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            total, used, free = get_disk_space(drive)
            if total > 0:
                drives_info.append((drive, total, used, free))
                pct = (used / total) * 100
                bar_len = 22
                filled = int(bar_len * used / total)
                bar = "█" * filled + "░" * (bar_len - filled)
                color = "lred" if pct > 90 else "lyellow" if pct > 70 else "lgreen"
                cprint(f"  {drive} [{bar}] {used:.0f}/{total:.0f} GB ({pct:.0f}%)", color)
    return drives_info


def get_gpu_info():
    """显卡信息"""
    print()
    cprint("  [ 显卡 GPU ]", "lyellow")
    try:
        r = run_cmd("wmic path win32_VideoController get Name /format:csv")
        if r:
            for line in r.strip().split("\n")[1:]:
                name = line.split(",")[-1].strip()
                if name:
                    print(f"  {name}")
    except Exception:
        print("  （无法获取）")


def get_activation():
    """Windows 激活状态"""
    print()
    cprint("  [ 激活状态 ]", "lyellow")
    try:
        r = run_cmd('cscript //nologo "%SystemRoot%\\System32\\slmgr.vbs" /dli')
        if r:
            for line in r.split("\n"):
                line = line.strip()
                if line and not line.startswith("Windows Script"):
                    if "licensed" in line.lower() or "已许可" in line.lower():
                        cprint(f"  {line}", "lgreen")
                    else:
                        print(f"  {line}")
    except Exception:
        print("  （无法获取）")


def get_network():
    """网络信息"""
    print()
    cprint("  [ 网络 ]", "lyellow")
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"  主机名：{hostname}")
        print(f"  本机 IP：{ip}")
    except Exception:
        print("  （无法获取）")


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       系统信息检测工具", "lwhite")
    cprint(SEP, "lcyan")
    print()

    get_os_info()
    get_cpu_info()
    get_memory_info()
    drives_info = get_disk_info()
    get_gpu_info()
    get_activation()
    get_network()

    # 导出选项
    print()
    cprint("  " + SEP2, "lcyan")
    print("  是否导出系统信息报告到桌面？[Y/N]: ", end="")
    if input().strip().lower() in ("y", "yes"):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        fname = f"系统信息_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(desktop, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"系统信息报告\n生成时间：{datetime.datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"操作系统：{platform.system()} {platform.release()}\n")
            f.write(f"计算机名：{socket.gethostname()}\n")
            f.write(f"CPU 核心：{os.cpu_count()}\n")
            f.write(f"架构：{platform.architecture()[0]}\n\n")
            f.write("磁盘空间：\n")
            for drive, total, used, free in drives_info:
                f.write(f"  {drive} {used:.0f}/{total:.0f} GB ({(used/total)*100:.0f}%)\n")
        ok(f"已导出到：{path}")

    pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
