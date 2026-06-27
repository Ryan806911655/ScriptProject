"""
系统垃圾清理 — 深度清理 C 盘垃圾文件
"""

import os
import sys
from _utils import *


def clean_temp_files():
    """清理系统临时文件"""
    info("[1/7] 系统临时文件")
    dirs = [
        ("用户 Temp",       os.environ.get("TEMP", "")),
        ("Windows Temp",    r"C:\Windows\Temp"),
        ("预读文件",         r"C:\Windows\Prefetch"),
        ("Local Temp",      os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp")),
    ]
    total = 0
    for name, path in dirs:
        if path and os.path.exists(path):
            size = get_dir_size(path)
            n = safe_clean_dir(path)
            if n > 0:
                ok(f"{name} — {format_bytes(size)}（{n} 个文件）")
                total += size
            else:
                info(f"{name} — 无需清理")
    return total


def clean_update_cache():
    """清理 Windows Update 缓存"""
    info("[2/7] Windows Update 缓存")
    path = r"C:\Windows\SoftwareDistribution\Download"
    if os.path.exists(path):
        size = get_dir_size(path)
        n = safe_clean_dir(path)
        if n > 0:
            ok(f"已清理 {format_bytes(size)}")
            return size
    info("无需清理")
    return 0


def clean_recycle_bin():
    """清空回收站"""
    info("[3/7] 回收站")
    total = 0
    for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        p = f"{d}:\\$Recycle.Bin"
        if os.path.exists(p):
            total += get_dir_size(p)
    if total > 0:
        run_cmd("rd /s /q C:\\$Recycle.Bin", capture=False)
        for d in "DEFGHIJKLMNOPQRSTUVWXYZ":
            run_cmd(f"rd /s /q {d}:\\$Recycle.Bin", capture=False)
        ok(f"已清空（{format_bytes(total)}）")
    else:
        info("回收站为空")
    return total


def clean_browser_cache():
    """清理浏览器缓存"""
    info("[4/7] 浏览器缓存")
    local = os.environ.get("LOCALAPPDATA", "")
    browsers = {
        "Chrome":  os.path.join(local, r"Google\Chrome\User Data\Default\Cache\Cache_Data"),
        "Edge":    os.path.join(local, r"Microsoft\Edge\User Data\Default\Cache\Cache_Data"),
        "Firefox": os.path.join(local, r"Mozilla\Firefox\Profiles"),
    }
    total = 0
    for name, path in browsers.items():
        if os.path.exists(path):
            s = get_dir_size(path)
            n = safe_clean_dir(path)
            if n > 0:
                ok(f"{name} — {format_bytes(s)}")
                total += s
            else:
                info(f"{name} — 无需清理")
        else:
            info(f"{name} — 未安装")
    return total


def clean_error_reports():
    """清理 Windows 错误报告"""
    info("[5/7] 错误报告 & 崩溃转储")
    paths = [
        r"C:\ProgramData\Microsoft\Windows\WER\ReportArchive",
        r"C:\ProgramData\Microsoft\Windows\WER\ReportQueue",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"CrashDumps"),
    ]
    total = 0
    for p in paths:
        if os.path.exists(p):
            s = get_dir_size(p)
            n = safe_clean_dir(p)
            if n > 0:
                ok(f"{os.path.basename(p)} — {format_bytes(s)}")
                total += s
    if total == 0:
        info("无需清理")
    return total


def clean_other():
    """其他清理"""
    info("[6/7] DNS & 缩略图缓存")
    run_cmd("ipconfig /flushdns", capture=False)
    ok("DNS 缓存已刷新")

    thumb = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         r"Microsoft\Windows\Explorer")
    cleaned = 0
    if os.path.isdir(thumb):
        for f in os.listdir(thumb):
            if f.lower().startswith(("thumbcache", "iconcache")):
                try:
                    cleaned += os.path.getsize(os.path.join(thumb, f))
                    os.remove(os.path.join(thumb, f))
                except (OSError, PermissionError):
                    pass
    if cleaned > 0:
        ok(f"缩略图缓存 — {format_bytes(cleaned)}")
    else:
        info("缩略图缓存 — 无需清理")
    return cleaned


def clean_disk_cleanup():
    """调用系统磁盘清理"""
    info("[7/7] 系统磁盘清理工具")
    try:
        run_cmd("cleanmgr /sagerun:1", capture=False)
        ok("已调用")
    except Exception:
        info("跳过")


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       系统垃圾清理工具", "lwhite")
    cprint(SEP, "lcyan")
    print()

    require_admin()

    total, used, free = get_disk_space("C:")
    print(f"  C盘：总计 {total:.1f} GB | 已用 {used:.1f} GB | 剩余 {free:.1f} GB")
    print()

    print("  [1] 扫描模式 — 仅统计，不删除（推荐首次使用）")
    print("  [2] 清理模式 — 直接清理")
    print("  [0] 退出")
    print()
    choice = input("  请选择（默认 1）: ").strip()
    if choice == "0":
        info("已取消")
        return

    scan_only = choice != "2"
    print()
    if scan_only:
        info(">>> 扫描模式 <<< 仅统计可清理空间")
    else:
        warn(">>> 清理模式 <<< 将永久删除垃圾文件！")
        if input("  确认？[Y/N]: ").strip().lower() not in ("y", "yes"):
            info("已取消")
            return

    print()
    total_cleaned = 0
    total_cleaned += clean_temp_files()
    total_cleaned += clean_update_cache()
    total_cleaned += clean_recycle_bin()
    total_cleaned += clean_browser_cache()
    total_cleaned += clean_error_reports()
    total_cleaned += clean_other()
    if not scan_only:
        clean_disk_cleanup()

    print()
    cprint(SEP, "lgreen")
    if scan_only:
        cprint(f"  扫描完成！共可清理约 {format_bytes(total_cleaned)}", "lcyan")
        info("重新运行并选择「清理模式」即可释放空间")
    else:
        _, _, new_free = get_disk_space("C:")
        cprint(f"  清理完成！共释放约 {format_bytes(total_cleaned)}", "lgreen")
        ok(f"C盘剩余：{new_free:.1f} GB (+{new_free - free:.1f} GB)")
        info("建议重启电脑以彻底完成清理")
    cprint(SEP, "lgreen")
    pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
