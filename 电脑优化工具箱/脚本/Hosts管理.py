"""
Hosts 文件管理 — 查看/备份/切换预设方案
"""

import os
import sys
import shutil
import datetime
from _utils import *

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hosts_backups")

# 预设方案
PRESETS = {
    "1": {
        "name": "GitHub 加速",
        "desc": "优化 GitHub 访问速度（含 github.com / github.io / assets 等）",
        "entries": [
            "# === GitHub 加速 ===",
            "140.82.112.4    github.com",
            "140.82.112.4    gist.github.com",
            "199.232.96.133  raw.githubusercontent.com",
            "199.232.96.133  gist.githubusercontent.com",
            "199.232.96.133  cloud.githubusercontent.com",
            "199.232.96.133  camo.githubusercontent.com",
            "199.232.96.133  avatars.githubusercontent.com",
            "199.232.96.133  avatars0.githubusercontent.com",
            "199.232.96.133  avatars1.githubusercontent.com",
            "199.232.96.133  avatars2.githubusercontent.com",
            "199.232.96.133  avatars3.githubusercontent.com",
            "199.232.96.133  avatars4.githubusercontent.com",
            "199.232.96.133  avatars5.githubusercontent.com",
            "199.232.96.133  user-images.githubusercontent.com",
            "185.199.108.153 assets-cdn.github.com",
            "185.199.109.153 assets-cdn.github.com",
            "185.199.110.153 assets-cdn.github.com",
            "185.199.111.153 assets-cdn.github.com",
            "185.199.108.154  github.githubassets.com",
            "185.199.109.154  github.githubassets.com",
            "185.199.110.154  github.githubassets.com",
            "185.199.111.154  github.githubassets.com",
        ],
    },
    "2": {
        "name": "开发者通用",
        "desc": "GitHub + StackOverflow + npm + pip 等常用开发站点",
        "entries": [
            "# === GitHub ===",
            "140.82.112.4    github.com",
            "199.232.96.133  raw.githubusercontent.com",
            "# === StackOverflow ===",
            "151.101.1.69    stackoverflow.com",
            "151.101.1.69    stackexchange.com",
            "151.101.1.69    serverfault.com",
            "151.101.1.69    superuser.com",
            "151.101.1.69    askubuntu.com",
            "# === npm ===",
            "104.16.27.34    registry.npmjs.org",
            "# === PyPI ===",
            "151.101.0.223   pypi.org",
            "151.101.0.223   files.pythonhosted.org",
            "# === Docker ===",
            "13.224.207.78   registry-1.docker.io",
            "13.224.207.78   hub.docker.com",
        ],
    },
    "3": {
        "name": "屏蔽广告 & 跟踪",
        "desc": "屏蔽常见广告/统计/跟踪域名（约 50+ 条）",
        "entries": [
            "# === 广告 & 跟踪屏蔽 ===",
            "0.0.0.0  doubleclick.net",
            "0.0.0.0  ad.doubleclick.net",
            "0.0.0.0  googleadservices.com",
            "0.0.0.0  www.googleadservices.com",
            "0.0.0.0  googlesyndication.com",
            "0.0.0.0  pagead2.googlesyndication.com",
            "0.0.0.0  adservice.google.com",
            "0.0.0.0  adservice.google.com.hk",
            "0.0.0.0  analytics.google.com",
            "0.0.0.0  ssl.google-analytics.com",
            "0.0.0.0  www.google-analytics.com",
            "0.0.0.0  adsense.google.com",
            "0.0.0.0  cdn.ampproject.org",
            "0.0.0.0  ads.yahoo.com",
            "0.0.0.0  adserver.yahoo.com",
            "0.0.0.0  ads.msn.com",
            "0.0.0.0  ads.facebook.com",
            "0.0.0.0  pixel.facebook.com",
            "0.0.0.0  ads.twitter.com",
            "0.0.0.0  analytics.twitter.com",
            "0.0.0.0  baidu.com",
            "0.0.0.0  hm.baidu.com",
            "0.0.0.0  cpro.baidu.com",
            "0.0.0.0  pos.baidu.com",
            "0.0.0.0  eclick.baidu.com",
            "0.0.0.0  union.baidu.com",
            "0.0.0.0  alimama.cn",
            "0.0.0.0  tanx.com",
            "0.0.0.0  mmstat.com",
            "0.0.0.0  cnzz.com",
            "0.0.0.0  s4.cnzz.com",
            "0.0.0.0  umeng.com",
            "0.0.0.0  api.umeng.com",
            "0.0.0.0  admaster.com.cn",
            "0.0.0.0  miaozhen.com",
        ],
    },
}


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def read_hosts():
    """读取 hosts 文件"""
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        err(f"读取失败：{e}")
        return None


def write_hosts(content):
    """写入 hosts 文件"""
    try:
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        # 刷新 DNS 使生效
        run_cmd("ipconfig /flushdns", capture=False)
        return True
    except Exception as e:
        err(f"写入失败：{e}（请确认以管理员权限运行）")
        return False


def backup_hosts():
    """备份当前 hosts"""
    ensure_backup_dir()
    content = read_hosts()
    if content is None:
        return None
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"hosts_backup_{ts}"
    path = os.path.join(BACKUP_DIR, fname)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
    except Exception as e:
        err(f"备份失败：{e}")
        return None


def list_backups():
    """列出备份"""
    ensure_backup_dir()
    files = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("hosts_backup_")],
        reverse=True
    )
    return [os.path.join(BACKUP_DIR, f) for f in files]


def apply_preset(preset_key):
    """应用预设方案（追加到现有 hosts 末尾）"""
    preset = PRESETS.get(preset_key)
    if not preset:
        return False

    current = read_hosts()
    if current is None:
        return False

    # 检查是否有旧的相同预设（按标记行查找）
    marker = preset["entries"][0]
    if marker in current:
        warn("该预设可能已存在，将跳过重复添加")

    # 追加
    new_content = current.rstrip("\n") + "\n\n" + "\n".join(preset["entries"]) + "\n"
    return write_hosts(new_content)


def clear_custom():
    """清除自定义条目，恢复到系统默认"""
    warn("这将清除 hosts 中所有非默认内容！")
    print()
    if input("  确认清除？[Y/N]: ").strip().lower() not in ("y", "yes"):
        return False

    default = (
        "# Copyright (c) 1993-2009 Microsoft Corp.\n"
        "#\n"
        "# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n"
        "#\n"
        "# This file contains the mappings of IP addresses to host names.\n"
        "# Each entry should be kept on an individual line.\n"
        "# The IP address should be placed in the first column\n"
        "# followed by the corresponding host name.\n"
        "# The IP address and the host name should be separated by\n"
        "# at least one space.\n"
        "#\n"
        "# Additionally, comments (such as these) may be inserted\n"
        "# on individual lines or following the machine name denoted by\n"
        "# a '#' symbol.\n"
        "#\n"
        "# For example:\n"
        "#\n"
        "#      102.54.94.97     rhino.acme.com          # source server\n"
        "#       38.25.63.10     x.acme.com              # x client host\n"
        "#\n"
        "# localhost name resolution is handled within DNS itself.\n"
        "#\t127.0.0.1       localhost\n"
        "#\t::1             localhost\n"
        "127.0.0.1       localhost\n"
        "::1             localhost\n"
    )
    return write_hosts(default)


# ---------- 主流程 ----------
def main():
    require_admin()

    while True:
        cprint(SEP, "lcyan")
        cprint("       Hosts 文件管理", "lwhite")
        cprint(SEP, "lcyan")
        print()

        # 显示当前 hosts 概况
        content = read_hosts()
        if content:
            lines = [l for l in content.split("\n") if l.strip() and not l.strip().startswith("#")]
            print(f"  当前条目数：{len(lines)} 行")
            print(f"  hosts 大小：{format_bytes(len(content.encode('utf-8')))}")
            if lines:
                print()
                print("  当前生效条目：")
                for line in lines[:10]:
                    print(f"    {line[:75]}")
                if len(lines) > 10:
                    print(f"    ... 还有 {len(lines) - 10} 行")
        print()

        print("  [1] 查看完整 hosts")
        print("  [2] 备份当前 hosts")
        print("  [3] 应用预设方案（GitHub加速/开发者/去广告）")
        print("  [4] 从备份恢复")
        print("  [5] 清除自定义 → 恢复默认")
        print("  [6] 用记事本手动编辑")
        print("  [0] 返回上级")
        print()

        choice = input("  请选择: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            print()
            cprint("  " + SEP2, "lcyan")
            if content:
                print(content)
            cprint("  " + SEP2, "lcyan")
            pause()

        elif choice == "2":
            path = backup_hosts()
            if path:
                ok(f"已备份到：{path}")
            pause()

        elif choice == "3":
            print()
            for key, preset in PRESETS.items():
                print(f"  [{key}] {preset['name']} — {preset['desc']}")
            print("  [0] 返回")
            print()
            pk = input("  请选择方案: ").strip()
            if pk in PRESETS:
                # 先自动备份
                backup_path = backup_hosts()
                if backup_path:
                    ok(f"已自动备份：{os.path.basename(backup_path)}")
                if apply_preset(pk):
                    ok(f"已应用「{PRESETS[pk]['name']}」")
                    info("DNS 缓存已刷新，立即生效")
                else:
                    err("应用失败")
            pause()

        elif choice == "4":
            backups = list_backups()
            if not backups:
                info("没有备份文件")
                pause()
                continue
            print()
            for idx, bp in enumerate(backups, 1):
                fname = os.path.basename(bp)
                size = format_bytes(os.path.getsize(bp))
                print(f"  [{idx}] {fname} ({size})")
            print("  [0] 返回")
            print()
            bi = input("  请选择要恢复的备份: ").strip()
            try:
                bi = int(bi)
                if 1 <= bi <= len(backups):
                    with open(backups[bi - 1], "r", encoding="utf-8") as f:
                        restored = f.read()
                    if write_hosts(restored):
                        ok("已恢复")
            except ValueError:
                pass
            pause()

        elif choice == "5":
            if clear_custom():
                ok("已恢复到系统默认")
            pause()

        elif choice == "6":
            info("正在用记事本打开 hosts...")
            os.system(f'notepad "{HOSTS_PATH}"')
            info("编辑完成后请保存，DNS 会自动刷新")
            run_cmd("ipconfig /flushdns", capture=False)
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
