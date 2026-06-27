"""
端口 & 进程管理 — 查看端口占用/定位进程/一键释放
"""

import os
import sys
import subprocess
from _utils import *


def get_listening_ports():
    """获取所有监听端口及对应进程"""
    try:
        r = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, encoding="gbk", errors="replace", timeout=15
        )
        lines = r.stdout.strip().split("\n")
        ports = []
        for line in lines[4:]:  # 跳过表头
            parts = line.split()
            if len(parts) >= 5 and parts[3].endswith(":") == False:
                proto = parts[0]
                local = parts[1]
                foreign = parts[2]
                state = parts[3] if len(parts) >= 5 else ""
                pid = parts[-1]

                # 提取端口号
                if ":" in local:
                    port = local.split(":")[-1]
                    addr = ":".join(local.split(":")[:-1])
                else:
                    continue

                if state in ("LISTENING", "ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT"):
                    ports.append({
                        "proto": proto,
                        "address": addr,
                        "port": port,
                        "state": state,
                        "pid": pid,
                    })
        return ports
    except Exception as e:
        err(f"获取端口信息失败：{e}")
        return []


def get_process_info(pid):
    """获取进程详细信息"""
    try:
        # 用 wmic 获取进程名
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, encoding="gbk", errors="replace", timeout=10
        )
        if r.stdout.strip():
            parts = r.stdout.strip().replace('"', '').split(",")
            if len(parts) >= 2:
                return {
                    "name": parts[0].strip(),
                    "pid": pid,
                    "memory": parts[-1].strip() if len(parts) >= 5 else "?",
                }
    except Exception:
        pass
    return {"name": "?", "pid": pid, "memory": "?"}


def kill_process(pid, force=False):
    """结束进程"""
    flag = "/F" if force else ""
    try:
        r = subprocess.run(
            ["taskkill", "/PID", str(pid), flag],
            capture_output=True, text=True, encoding="gbk", errors="replace", timeout=15
        )
        if r.returncode == 0:
            return True, "已终止"
        else:
            return False, r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return False, str(e)


def kill_by_port(port):
    """根据端口结束进程"""
    ports = get_listening_ports()
    for p in ports:
        if p["port"] == str(port) and p["state"] == "LISTENING":
            ok, msg = kill_process(p["pid"])
            return ok, p["pid"], msg
    return False, None, "端口未被占用"


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       端口 & 进程管理", "lwhite")
    cprint(SEP, "lcyan")
    print()

    while True:
        print("  [1] 查看所有监听端口")
        print("  [2] 查找占用指定端口的进程")
        print("  [3] 一键释放端口（输入端口号）")
        print("  [4] 根据 PID 结束进程")
        print("  [0] 返回上级")
        print()

        choice = input("  请选择: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            print()
            info("正在获取端口信息...")
            ports = get_listening_ports()
            if not ports:
                info("未获取到端口信息")
                pause()
                continue

            # 按端口号排序
            ports.sort(key=lambda x: int(x["port"]) if x["port"].isdigit() else 0)

            # 去重显示（每个端口只显示一次，优先 LISTENING）
            shown = {}
            for p in ports:
                key = (p["port"], p["proto"])
                if key not in shown or p["state"] == "LISTENING":
                    shown[key] = p

            cprint(f"  共 {len(shown)} 个监听/活动端口：", "lcyan")
            print()
            print(f"  {'协议':<6} {'地址':<20} {'端口':<8} {'状态':<14} {'PID':<8} {'进程'}")
            print(f"  {'-'*6} {'-'*20} {'-'*8} {'-'*14} {'-'*8} {'-'*20}")

            for p in shown.values():
                proc = get_process_info(p["pid"])
                state_color = "lgreen" if p["state"] == "LISTENING" else "lyellow"
                print(f"  {p['proto']:<6} {p['address']:<20} {p['port']:<8} ", end="")
                cprint(f"{p['state']:<14} ", state_color, end="")
                print(f"{p['pid']:<8} {proc['name']}")

            pause()

        elif choice == "2":
            port = input("  请输入端口号: ").strip()
            if not port:
                continue
            print()
            ports = get_listening_ports()
            found = [p for p in ports if p["port"] == port]

            if not found:
                info(f"端口 {port} 未被占用")
                pause()
                continue

            for p in found:
                proc = get_process_info(p["pid"])
                cprint(f"  端口 {port} [{p['proto']}] {p['state']}", "lyellow")
                print(f"  PID：{p['pid']}")
                print(f"  进程：{proc['name']}")
                print(f"  内存：{proc['memory']}")

                # 问是否结束
                print()
                if input("  是否结束此进程？[Y/N]: ").strip().lower() in ("y", "yes"):
                    ok_flag, msg = kill_process(p["pid"])
                    if ok_flag:
                        ok("已终止")
                    else:
                        # 强制结束
                        print(f"  普通终止失败：{msg}")
                        if input("  是否强制结束？[Y/N]: ").strip().lower() in ("y", "yes"):
                            ok_flag, msg = kill_process(p["pid"], force=True)
                            if ok_flag:
                                ok("已强制终止")
                            else:
                                err(f"强制终止失败：{msg}")
            pause()

        elif choice == "3":
            port = input("  请输入要释放的端口号: ").strip()
            if not port:
                continue
            print()
            ok_flag, pid, msg = kill_by_port(port)
            if ok_flag:
                ok(f"端口 {port} 已释放（进程 PID={pid}）")
            else:
                warn(msg)
            pause()

        elif choice == "4":
            pid = input("  请输入 PID: ").strip()
            if not pid:
                continue
            proc = get_process_info(pid)
            print()
            print(f"  进程名：{proc['name']}")
            print(f"  PID：{proc['pid']}")
            print()
            if input("  确认结束此进程？[Y/N]: ").strip().lower() in ("y", "yes"):
                ok_flag, msg = kill_process(pid)
                if ok_flag:
                    ok("已终止")
                else:
                    print(f"  普通终止失败：{msg}")
                    if input("  强制结束？[Y/N]: ").strip().lower() in ("y", "yes"):
                        ok_flag, msg = kill_process(pid, force=True)
                        if ok_flag:
                            ok("已强制终止")
                        else:
                            err(f"失败：{msg}")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
