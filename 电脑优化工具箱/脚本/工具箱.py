"""
电脑优化工具箱 V2.0 — 主菜单
"""

import os
import sys
import socket
import importlib
from _utils import *

VERSION = "V2.0"

TOOLS = [
    ("清理垃圾",   "清理电脑垃圾",   "深度清理 C 盘垃圾文件，释放磁盘空间"),
    ("管理自启动", "管理自启动",     "扫描/禁用不必要的开机自启动软件"),
    ("释放性能",   "释放电脑性能",   "高性能电源/关特效/释放内存/禁服务"),
    ("网络修复",   "一键网络修复",   "DNS刷新/IP重置/代理检测/连通性测试"),
    ("系统信息",   "系统信息检测",   "查看硬件配置/系统版本/导出报告"),
    ("开荒优化",   "新机开荒优化",   "关遥测/去广告/卸预装/隐私设置"),
    ("开发环境",   "编程环境配置",   "Node.js/pip/Git 一键配置 & 镜像"),
    ("下载工具",   "常用工具下载",   "VM虚拟机/系统镜像/开发工具下载"),
    ("Hosts管理",  "Hosts 文件管理", "查看/备份/切换 hosts（GitHub加速/去广告）"),
    ("重复文件",   "重复文件扫描",   "MD5哈希扫描重复文件，释放磁盘空间"),
    ("端口进程",   "端口 & 进程管理","查看端口占用/定位进程/一键释放端口"),
    ("文件重命名", "文件批量重命名", "序号/前缀后缀/替换/正则/扩展名修改"),
]


def run_tool(module_name):
    """动态加载并运行工具模块"""
    try:
        mod = importlib.import_module(module_name)
        mod.main()
        return True
    except Exception as e:
        err(f"运行失败：{e}")
        pause()
        return True


def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print()
    cprint("  ╔══════════════════════════════════════════════╗", "lcyan")
    cprint("  ║                                              ║", "lcyan")
    cprint(f"  ║     电脑优化工具箱 {VERSION}                      ║", "lwhite")
    cprint("  ║     12 合 1 常用系统维护工具                 ║", "lcyan")
    cprint("  ║                                              ║", "lcyan")
    cprint("  ╚══════════════════════════════════════════════╝", "lcyan")
    print()

    try:
        hostname = socket.gethostname()
        _, _, c_free = get_disk_space("C:")
        print(f"  计算机：{hostname}    C盘剩余：{c_free:.1f} GB    "
              f"CPU：{os.cpu_count()} 核")
    except Exception:
        pass
    print()


def show_menu():
    cprint("  " + SEP2, "lcyan")
    for idx, (mod, name, desc) in enumerate(TOOLS, 1):
        # 编号固定 4 字符宽：[ 1] ~ [12]
        num = f"[{idx:>2}]"
        print(f"   {num} ", end="")
        # 名称补齐到 16 显示宽度
        cprint(pad_display(name, 16), "lwhite", end="")
        print(f"  —  {desc}")
    cprint("  " + SEP2, "lcyan")
    print()
    print("    [0]  退出")
    print()


def main():
    require_admin()

    try:
        if os.name == "nt":
            os.system("chcp 65001 > nul")
            os.system(f"title 电脑优化工具箱 {VERSION}")
    except Exception:
        pass

    while True:
        show_banner()
        show_menu()
        choice = input("  请输入功能编号 [0-12]: ").strip()

        if choice == "0":
            break
        elif choice in [str(i) for i in range(1, len(TOOLS) + 1)]:
            idx = int(choice) - 1
            mod_name = TOOLS[idx][0]
            run_tool(mod_name)
        else:
            cprint("  无效选择，请重新输入。", "lred")
            import time
            time.sleep(1)

    print()
    cprint(f"  感谢使用！", "lgreen")
    print()
    import time
    time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
