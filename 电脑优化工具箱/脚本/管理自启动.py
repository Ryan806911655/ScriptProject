"""
开机自启动管理 — 扫描/分析/禁用不必要的自启动程序
"""

import os
import sys
import datetime
import winreg
from _utils import *


# 已知系统项（不建议禁用）
SYSTEM_KEYS = [
    "securityhealth", "windows defender", "onedrive",
    "rtkoposdx", "igfxtray", "hotkeyscmds", "persistence",
    "rthdcpl", "sndvol", "avast", "kaspersky",
]

# 常见可安全禁用的第三方软件
SAFE_TO_DISABLE = [
    "wechat", "qq", "dingtalk", "baidu", "360", "sogou",
    "wps", "adobe", "google update", "skype", "spotify",
    "discord", "steam", "epic", "cloudmusic", "kuwo",
    "qqmusic", "youku", "iqiyi", "thunder", "alibaba",
    "teamviewer", "anydesk", "dropbox", "chrone", "qqpcmgr",
    "safeguard", "kxescore", "douyin", "kuaishou",
]


def scan_startup_items():
    """扫描所有开机启动项"""
    items = []

    # 注册表 Run 键
    for hkey_root, reg_path, label in [
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\Run", "注册表-当前用户"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\Microsoft\Windows\CurrentVersion\Run", "注册表-本机"),
    ]:
        try:
            with winreg.OpenKey(hkey_root, reg_path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        items.append({
                            "name": name, "command": value,
                            "source": label, "key_root": hkey_root,
                            "key_path": reg_path, "type": "registry",
                        })
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass

    # 启动文件夹
    for folder_label, folder_path in [
        ("启动文件夹-用户", os.path.join(os.environ.get("APPDATA", ""),
         r"Microsoft\Windows\Start Menu\Programs\Startup")),
        ("启动文件夹-公共", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"),
    ]:
        if os.path.isdir(folder_path):
            try:
                for fname in os.listdir(folder_path):
                    items.append({
                        "name": fname, "command": os.path.join(folder_path, fname),
                        "source": folder_label, "path": os.path.join(folder_path, fname),
                        "type": "shortcut",
                    })
            except (PermissionError, FileNotFoundError):
                pass

    return items


def classify(item):
    """分类：system / safe_to_disable / unknown"""
    lower = (item["name"] + " " + item["command"]).lower()
    for kw in SYSTEM_KEYS:
        if kw in lower:
            return "system", kw
    for kw in SAFE_TO_DISABLE:
        if kw in lower:
            return "safe", kw
    return "unknown", ""


def disable_registry(item):
    """禁用注册表启动项"""
    try:
        with winreg.OpenKey(item["key_root"], item["key_path"],
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, item["name"])
        return True
    except Exception:
        return False


def disable_shortcut(item):
    """移动快捷方式到备份文件夹"""
    try:
        backup = os.path.join(os.path.expanduser("~"), "Desktop", "已禁用的启动项备份")
        os.makedirs(backup, exist_ok=True)
        os.rename(item["path"], os.path.join(backup, item["name"]))
        return True, backup
    except Exception as e:
        return False, str(e)


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       开机自启动管理工具", "lwhite")
    cprint(SEP, "lcyan")
    print()

    require_admin()

    info("正在扫描开机启动项...")
    items = scan_startup_items()

    if not items:
        info("未发现任何开机启动项")
        pause()
        return

    # 分类
    sys_items, safe_items, unknown_items = [], [], []
    for item in items:
        cat, _ = classify(item)
        if cat == "system":
            sys_items.append(item)
        elif cat == "safe":
            safe_items.append(item)
        else:
            unknown_items.append(item)

    ok(f"共发现 {len(items)} 个开机启动项\n")
    print(f"  ┌─ 系统核心项（不建议禁）：{len(sys_items)} 个")
    print(f"  ├─ 可安全禁用的软件：      {len(safe_items)} 个")
    print(f"  └─ 未分类项目：            {len(unknown_items)} 个")
    print()

    # 显示可禁用的
    if safe_items:
        cprint("  >> 以下软件可以安全禁用，加快开机速度：", "lyellow")
        print()
        for idx, item in enumerate(safe_items, 1):
            name = item["name"][:45]
            cmd = item["command"]
            if len(cmd) > 55:
                cmd = cmd[:52] + "..."
            print(f"  [{idx}] {name}")
            print(f"      {cmd}")
            print()

    # 显示未分类
    if unknown_items:
        cprint("  >> 以下项目请自行判断是否可以禁用：", "lcyan")
        print()
        start_idx = len(safe_items)
        for idx, item in enumerate(unknown_items, start_idx + 1):
            name = item["name"][:45]
            cmd = item["command"]
            if len(cmd) > 55:
                cmd = cmd[:52] + "..."
            print(f"  [{idx}] {name}")
            print(f"      来源：{item['source']}")
            print(f"      {cmd}")
            print()

    # 菜单
    cprint("  " + SEP2, "lcyan")
    print("  [A] 一键禁用所有建议关闭的软件（推荐）")
    print("  [D] 手动选择要禁用的项目")
    print("  [E] 导出启动项报告到桌面")
    print("  [0] 退出")
    print()

    choice = input("  请选择（默认 A）: ").strip().lower()

    if choice == "0":
        return
    elif choice == "e":
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        fname = f"启动项报告_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(desktop, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"开机启动项报告 — {datetime.datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            for item in items:
                cat, _ = classify(item)
                tag = "[系统]" if cat == "system" else "[可禁]" if cat == "safe" else ""
                f.write(f"{tag} {item['name']}\n")
                f.write(f"  来源：{item['source']}\n")
                f.write(f"  命令：{item['command']}\n\n")
        ok(f"已导出到：{path}")
        pause()
        return
    elif choice == "d":
        all_display = safe_items + unknown_items
        if not all_display:
            info("没有可禁用的项目")
            pause()
            return
        nums = input("  输入要禁用的编号（逗号分隔，如 1,3,5）: ").strip()
        targets = []
        for p in nums.split(","):
            try:
                n = int(p.strip())
                if 1 <= n <= len(all_display):
                    targets.append(all_display[n - 1])
            except ValueError:
                pass
        if not targets:
            info("未输入有效编号")
            pause()
            return
    else:
        targets = safe_items

    if not targets:
        info("没有需要禁用的项目")
        pause()
        return

    print()
    warn(f"即将禁用 {len(targets)} 个启动项：")
    for t in targets:
        print(f"    - {t['name']}")
    print()
    if input("  确认执行？[Y/N]: ").strip().lower() not in ("y", "yes"):
        info("已取消")
        pause()
        return

    ok_count, fail_count = 0, 0
    for item in targets:
        print(f"  禁用：{item['name']}...", end=" ")
        if item["type"] == "registry":
            if disable_registry(item):
                cprint("OK", "lgreen")
                ok_count += 1
            else:
                cprint("失败", "lred")
                fail_count += 1
        else:
            success, info_msg = disable_shortcut(item)
            if success:
                cprint("OK", "lgreen")
                ok_count += 1
            else:
                cprint(f"失败（{info_msg}）", "lred")
                fail_count += 1

    print()
    ok(f"完成！成功禁用 {ok_count} 个，失败 {fail_count} 个")
    if ok_count > 0:
        info("已禁用的快捷方式备份在桌面的「已禁用的启动项备份」文件夹")
        info("重启电脑后生效")
    pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
