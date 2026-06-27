"""
网络一键修复 — DNS/IP/Winsock/防火墙/代理/连通性检测
"""

import os
import sys
import socket
import subprocess
from _utils import *


def fix_ip_dns():
    """释放并更新 IP，刷新 DNS"""
    info("[1/6] IP 地址 & DNS 缓存")
    steps = [
        ("释放 IP",    "ipconfig /release"),
        ("更新 IP",    "ipconfig /renew"),
        ("刷新 DNS",   "ipconfig /flushdns"),
    ]
    for name, cmd in steps:
        print(f"  {name}...", end=" ")
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True, encoding="gbk", errors="replace", timeout=15)
            cprint("OK", "lgreen") if r.returncode == 0 else cprint("完成", "lyellow")
        except subprocess.TimeoutExpired:
            cprint("超时", "lyellow")
        except Exception as e:
            cprint(f"失败", "lred")


def fix_winsock_tcp():
    """重置 Winsock 和 TCP/IP 协议栈"""
    info("[2/6] Winsock & TCP/IP 协议栈")
    steps = [
        ("Winsock 重置",  "netsh winsock reset"),
        ("TCP/IP 重置",   "netsh int ip reset"),
    ]
    for name, cmd in steps:
        print(f"  {name}...", end=" ")
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True, encoding="gbk", errors="replace", timeout=30)
            cprint("OK", "lgreen") if r.returncode == 0 else cprint("完成", "lyellow")
        except subprocess.TimeoutExpired:
            cprint("超时", "lyellow")


def fix_firewall_arp():
    """重置防火墙 & 清除 ARP"""
    info("[3/6] 防火墙 & ARP 缓存")
    for name, cmd in [
        ("防火墙重置", "netsh advfirewall reset"),
        ("ARP 缓存",   "arp -d *"),
    ]:
        print(f"  {name}...", end=" ")
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True, encoding="gbk", errors="replace", timeout=30)
            cprint("OK", "lgreen") if r.returncode == 0 else cprint("完成", "lyellow")
        except Exception:
            cprint("跳过", "lyellow")


def fix_proxy():
    """检查并关闭系统代理"""
    info("[4/6] 代理设置")
    try:
        r = run_cmd(
            'reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable'
        )
        if r and "0x1" in r:
            warn("系统代理已开启，正在关闭...")
            run_cmd(
                'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
            )
            ok("已关闭")
        else:
            ok("代理未开启")
    except Exception:
        info("跳过")


def check_hosts():
    """检查 hosts 文件"""
    info("[5/6] hosts 文件")
    path = r"C:\Windows\System32\drivers\etc\hosts"
    try:
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 50000:
                warn(f"hosts 文件较大（{format_bytes(size)}），建议检查是否有异常条目")
            else:
                ok(f"正常（{format_bytes(size)}）")
    except Exception:
        info("跳过")


def check_connectivity():
    """检测网络连通性"""
    info("[6/6] 网络连通性")
    targets = [
        ("114.114.114.114", "国内 DNS"),
        ("www.baidu.com",   "百度"),
        ("8.8.8.8",         "Google DNS"),
        ("github.com",      "GitHub"),
    ]
    for host, desc in targets:
        print(f"  ping {desc} ({host})...", end=" ")
        try:
            r = subprocess.run(
                ["ping", "-n", "1", "-w", "3000", host],
                capture_output=True, text=True, timeout=5
            )
            if "TTL=" in r.stdout or "ttl=" in r.stdout:
                cprint("通", "lgreen")
            else:
                cprint("不通", "lyellow")
        except subprocess.TimeoutExpired:
            cprint("超时", "lyellow")

    # 显示本机 IP
    print()
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        info(f"主机名：{hostname}  |  本机 IP：{ip}")
    except Exception:
        pass


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       网络一键修复工具", "lwhite")
    cprint(SEP, "lcyan")
    print()
    print("  将依次执行：")
    print("    1) 释放/更新 IP + 刷新 DNS")
    print("    2) 重置 Winsock + TCP/IP 协议栈")
    print("    3) 重置防火墙 + 清除 ARP")
    print("    4) 检查/关闭系统代理")
    print("    5) 检查 hosts 文件")
    print("    6) 网络连通性检测")
    print()

    require_admin()

    print()
    fix_ip_dns()
    print()
    fix_winsock_tcp()
    print()
    fix_firewall_arp()
    print()
    fix_proxy()
    print()
    check_hosts()
    print()
    check_connectivity()

    print()
    cprint(SEP, "lgreen")
    cprint("  网络修复完成！", "lgreen")
    warn("部分修复需要重启电脑才能生效")
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
