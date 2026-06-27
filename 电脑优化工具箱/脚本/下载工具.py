"""
常用工具下载 — VM虚拟机 / 系统镜像 / 开发工具
提供官方下载链接 + winget 一键安装
"""

import os
import sys
import subprocess
import webbrowser
from _utils import *


# ============================================================
# 下载资源列表
# ============================================================

# --- 虚拟机 ---
VM_RESOURCES = {
    "1": {
        "name": "VMware Workstation Pro 17",
        "desc": "功能最强的虚拟机（个人免费）",
        "url": "https://www.vmware.com/go/getworkstation-win",
        "winget": "VMware.WorkstationPro",
        "note": "安装后可用 Key: MC60H-DWHD6-H80U9-6V85M-8280D（仅供学习）",
    },
    "2": {
        "name": "VirtualBox",
        "desc": "开源免费虚拟机，轻量简单",
        "url": "https://www.virtualbox.org/wiki/Downloads",
        "winget": "Oracle.VirtualBox",
    },
}

# --- Windows 镜像（官方直链/下载页） ---
WINDOWS_ISOS = {
    "1": {
        "name": "Windows 11 官方下载",
        "desc": "微软官方媒体创建工具 / ISO",
        "url": "https://www.microsoft.com/software-download/windows11",
        "note": "推荐使用 Media Creation Tool 制作启动盘",
    },
    "2": {
        "name": "Windows 10 官方下载",
        "desc": "微软官方媒体创建工具 / ISO",
        "url": "https://www.microsoft.com/software-download/windows10",
    },
    "3": {
        "name": "Windows Server 2025 评估版",
        "desc": "180 天评估，微软官方",
        "url": "https://www.microsoft.com/en-us/evalcenter/download-windows-server-2025",
    },
}

# --- Linux 镜像 ---
LINUX_ISOS = {
    "1": {
        "name": "Ubuntu 24.04 LTS 桌面版",
        "desc": "最流行的 Linux 桌面发行版",
        "url": "https://releases.ubuntu.com/noble/ubuntu-24.04.2-desktop-amd64.iso",
        "note": "直接 ISO 下载链接（约 5.7 GB）",
        "alt_url": "https://ubuntu.com/download/desktop",
    },
    "2": {
        "name": "Ubuntu 24.04 LTS 服务器版",
        "desc": "无桌面，适合服务器/开发环境",
        "url": "https://releases.ubuntu.com/noble/ubuntu-24.04.2-live-server-amd64.iso",
    },
    "3": {
        "name": "Ubuntu 22.04 LTS 桌面版",
        "desc": "长期支持，更稳定",
        "url": "https://releases.ubuntu.com/jammy/ubuntu-22.04.5-desktop-amd64.iso",
    },
    "4": {
        "name": "Kali Linux",
        "desc": "渗透测试专用",
        "url": "https://www.kali.org/get-kali/#kali-installer-images",
    },
    "5": {
        "name": "CentOS Stream 9",
        "desc": "RHEL 兼容，服务器常用",
        "url": "https://mirrors.aliyun.com/centos-stream/9-stream/BaseOS/x86_64/iso/",
    },
}

# --- 开发工具 ---
DEV_TOOLS = {
    "1": {
        "name": "VS Code",
        "desc": "最流行的代码编辑器",
        "url": "https://code.visualstudio.com/download",
        "winget": "Microsoft.VisualStudioCode",
    },
    "2": {
        "name": "Git for Windows",
        "desc": "版本控制工具",
        "url": "https://git-scm.com/download/win",
        "winget": "Git.Git",
    },
    "3": {
        "name": "Node.js LTS",
        "desc": "JavaScript 运行时",
        "url": "https://nodejs.org/zh-cn/download/",
        "winget": "OpenJS.NodeJS.LTS",
    },
    "4": {
        "name": "Python 3.13",
        "desc": "Python 解释器",
        "url": "https://www.python.org/downloads/",
        "winget": "Python.Python.3.13",
    },
    "5": {
        "name": "JetBrains Toolbox",
        "desc": "管理 IntelliJ/PyCharm/WebStorm 等 IDE",
        "url": "https://www.jetbrains.com/toolbox-app/",
        "winget": "JetBrains.Toolbox",
    },
    "6": {
        "name": "Docker Desktop",
        "desc": "容器化开发环境",
        "url": "https://www.docker.com/products/docker-desktop/",
        "winget": "Docker.DockerDesktop",
    },
    "7": {
        "name": "Notepad++",
        "desc": "轻量文本编辑器",
        "url": "https://notepad-plus-plus.org/downloads/",
        "winget": "Notepad++.Notepad++",
    },
    "8": {
        "name": "7-Zip",
        "desc": "开源压缩工具",
        "url": "https://www.7-zip.org/download.html",
        "winget": "7zip.7zip",
    },
    "9": {
        "name": "Windows Terminal",
        "desc": "微软官方终端",
        "url": "https://aka.ms/terminal",
        "winget": "Microsoft.WindowsTerminal",
    },
}

# --- 其他实用工具 ---
OTHER_TOOLS = {
    "1": {
        "name": "Rufus",
        "desc": "USB 启动盘制作工具（装系统必备）",
        "url": "https://rufus.ie/zh/",
        "winget": "Rufus.Rufus",
    },
    "2": {
        "name": "CPU-Z",
        "desc": "CPU 检测工具",
        "url": "https://www.cpuid.com/softwares/cpu-z.html",
        "winget": "CPUID.CPU-Z",
    },
    "3": {
        "name": "Geek Uninstaller",
        "desc": "彻底卸载软件，不留残留",
        "url": "https://geekuninstaller.com/download",
    },
    "4": {
        "name": "Everything",
        "desc": "极速文件搜索",
        "url": "https://www.voidtools.com/zh-cn/downloads/",
        "winget": "voidtools.Everything",
    },
    "5": {
        "name": "Dism++",
        "desc": "强大的系统清理 & 优化工具",
        "url": "https://github.com/Chuyu-Team/Dism-Multi-language/releases",
    },
}


# ============================================================
# 通用下载/安装函数
# ============================================================

def open_download(item):
    """打开下载链接 / winget 安装"""
    print()
    print(f"  名称：{item['name']}")
    print(f"  说明：{item.get('desc', '')}")
    if item.get("note"):
        cprint(f"  提示：{item['note']}", "lyellow")
    print()

    # 如果有 winget 且用户想自动安装
    if item.get("winget"):
        print("  [1] 自动安装（winget）")
        print("  [2] 打开下载页面（浏览器）")
        print("  [0] 返回")
        print()
        choice = input("  请选择: ").strip()

        if choice == "0":
            return
        elif choice == "2":
            print()
            info("正在打开浏览器...")
            webbrowser.open(item["url"])
            ok(f"已打开：{item['url']}")
            return
        else:
            print()
            info(f"正在通过 winget 安装：{item['name']}...")
            try:
                subprocess.run(
                    ["winget", "install", item["winget"],
                     "--accept-package-agreements", "--accept-source-agreements"],
                    check=False
                )
                if subprocess.run(["winget", "list", item["winget"]],
                                  capture_output=True).returncode == 0:
                    ok("安装完成！")
                else:
                    info("请检查安装结果")
            except FileNotFoundError:
                warn("winget 不可用，改打开网页")
                webbrowser.open(item["url"])
            except Exception as e:
                err(f"安装失败：{e}")
                info("改打开下载页面...")
                webbrowser.open(item["url"])
            return

    # 没有 winget，直接打开网页
    print("  [1] 打开下载页面")
    print("  [0] 返回")
    print()
    if input("  请选择: ").strip() != "0":
        webbrowser.open(item["url"])
        ok(f"已打开：{item['url']}")


def show_list(items, title):
    """显示下载列表并处理选择"""
    while True:
        print()
        cprint(f"  [{title}]", "lyellow")
        print()
        for key, item in items.items():
            print(f"  [{key}] {item['name']} — {item.get('desc', '')}")
        print("  [0] 返回")
        print()
        choice = input("  请选择: ").strip()

        if choice == "0":
            return
        if choice in items:
            open_download(items[choice])
            pause()


# ============================================================
# 主菜单
# ============================================================

def main():
    while True:
        cprint(SEP, "lcyan")
        cprint("       常用工具下载 & 安装", "lwhite")
        cprint(SEP, "lcyan")
        print()
        print("  [1] 虚拟机 — VMware / VirtualBox")
        print("  [2] Windows 镜像 — Win10 / Win11 官方下载")
        print("  [3] Linux 镜像  — Ubuntu / Kali / CentOS")
        print("  [4] 开发工具   — VS Code / Git / Node.js / Python / Docker...")
        print("  [5] 实用工具   — Rufus / CPU-Z / Everything / Dism++...")
        print("  [0] 返回上级")
        print()

        choice = input("  请选择: ").strip()

        if choice == "0":
            return
        elif choice == "1":
            show_list(VM_RESOURCES, "虚拟机")
        elif choice == "2":
            show_list(WINDOWS_ISOS, "Windows 镜像")
        elif choice == "3":
            show_list(LINUX_ISOS, "Linux 镜像")
        elif choice == "4":
            show_list(DEV_TOOLS, "开发工具")
        elif choice == "5":
            show_list(OTHER_TOOLS, "实用工具")
        else:
            info("无效选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
