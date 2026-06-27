"""
电脑性能释放 — 一键优化：电源计划/视觉特效/内存/服务/启动
"""

import os
import sys
import time
import winreg
from _utils import *

# 尝试导入 psutil（可选依赖）
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def show_status():
    """显示当前系统状态"""
    if not HAS_PSUTIL:
        info("psutil 未安装，跳过性能检测（pip install psutil）")
        return
    print()
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:")
    print(f"  CPU：{cpu:.1f}%  |  内存：{mem.percent:.1f}% "
          f"({mem.used/(1024**3):.1f}/{mem.total/(1024**3):.1f} GB)")
    print(f"  C盘：{disk.percent:.1f}% ({disk.free/(1024**3):.1f} GB 可用)")
    print()


def opt_power_plan():
    """切换到高性能电源计划"""
    info("[1/8] 电源计划")
    plans = [
        ("8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "高性能"),
        ("e9a42b02-d5df-448d-aa00-03f14749eb61", "卓越性能"),
    ]
    for guid, name in plans:
        r = run_cmd(f"powercfg /setactive {guid}")
        if r == "":
            ok(f"已切换到「{name}」")
            return
    warn("切换失败，请手动设置")


def opt_visual():
    """关闭不必要的视觉特效"""
    info("[2/8] 视觉特效")
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
        ok("已设为「调整为最佳性能」")
    except Exception as e:
        warn(f"失败：{e}")
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Control Panel\Desktop\WindowMetrics",
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MinAnimate", 0, winreg.REG_SZ, "0")
        ok("已关闭窗口动画")
    except Exception:
        pass


def opt_transparency():
    """关闭透明效果"""
    info("[3/8] 透明效果")
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "EnableTransparency", 0, winreg.REG_DWORD, 0)
        ok("已关闭")
    except Exception as e:
        warn(f"失败：{e}")


def opt_cpu():
    """CPU 调度优化 — 优先前台程序"""
    info("[4/8] CPU 调度")
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\PriorityControl",
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 0x1A)
        ok("已设为「优先前台程序」")
    except Exception as e:
        warn(f"失败：{e}")


def opt_memory():
    """释放内存"""
    info("[5/8] 内存释放")
    if not HAS_PSUTIL:
        info("psutil 未安装，跳过（pip install psutil）")
        return

    mem_before = psutil.virtual_memory()
    print(f"  优化前：{mem_before.percent:.1f}%")

    try:
        k32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        for proc in psutil.process_iter(['pid']):
            try:
                h = k32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                if h:
                    psapi.EmptyWorkingSet(h)
                    k32.CloseHandle(h)
            except Exception:
                pass
        mem_after = psutil.virtual_memory()
        freed = mem_before.used - mem_after.used
        if freed > 10 * 1024 * 1024:
            ok(f"已释放 {freed/(1024**2):.0f} MB")
        else:
            ok("内存已处于较优状态")
    except Exception as e:
        warn(f"失败：{e}")


def opt_services():
    """禁用不必要的后台服务"""
    info("[6/8] 后台服务")
    services = {
        "DiagTrack":         ("诊断跟踪",        "disabled"),
        "dmwappushservice":  ("WAP 推送",         "disabled"),
        "MapsBroker":        ("地图管理",         "disabled"),
        "lfsvc":             ("地理位置",         "disabled"),
        "XboxNetApiSvc":     ("Xbox 网络",        "disabled"),
        "XblAuthManager":    ("Xbox 验证",        "disabled"),
        "XblGameSave":       ("Xbox 游戏存档",     "disabled"),
        "SysMain":           ("SuperFetch 预读",  "manual"),
        "WSearch":           ("Windows 搜索索引", "manual"),
        "Fax":               ("传真",             "disabled"),
        "TabletInputService":("触屏键盘",         "manual"),
    }
    n = 0
    for svc, (desc, start_type) in services.items():
        check = run_cmd(f"sc query {svc} 2>nul")
        if "FAILED" in check or "1060" in check:
            continue
        start_val = "disabled" if start_type == "disabled" else "demand"
        run_cmd(f"sc config {svc} start= {start_val}")
        run_cmd(f"net stop {svc} /y 2>nul")
        n += 1
    ok(f"已优化 {n} 个服务")


def opt_background_apps():
    """禁止应用后台运行"""
    info("[7/8] 后台应用")
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                              r"Software\Policies\Microsoft\Windows\AppPrivacy") as key:
            winreg.SetValueEx(key, "LetAppsRunInBackground", 0, winreg.REG_DWORD, 2)
        ok("已禁止")
    except Exception as e:
        warn(f"失败：{e}")


def opt_boot():
    """优化启动配置"""
    info("[8/8] 启动配置")
    try:
        run_cmd("bcdedit /timeout 5", capture=False)
        ok("启动超时 -> 5 秒")
    except Exception:
        pass
    try:
        run_cmd("bcdedit /set {current} numproc 0", capture=False)
        ok("已启用多核启动")
    except Exception:
        pass


# ---------- 优化项列表 ----------
OPTIMIZATIONS = [
    ("电源计划",      opt_power_plan),
    ("视觉特效",      opt_visual),
    ("透明效果",      opt_transparency),
    ("CPU 调度",      opt_cpu),
    ("内存释放",      opt_memory),
    ("后台服务",      opt_services),
    ("后台应用",      opt_background_apps),
    ("启动配置",      opt_boot),
]


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       电脑性能释放工具", "lwhite")
    cprint(SEP, "lcyan")
    print()

    require_admin()
    show_status()

    print("  将执行以下优化：")
    for idx, (name, _) in enumerate(OPTIMIZATIONS, 1):
        print(f"    {idx}. {name}")
    print()

    print("  [1] 一键自动优化（推荐）")
    print("  [2] 自定义选择")
    print("  [0] 退出")
    print()

    choice = input("  请选择（默认 1）: ").strip()
    if choice == "0":
        return

    enabled = list(range(len(OPTIMIZATIONS)))
    if choice == "2":
        print()
        for idx, (name, _) in enumerate(OPTIMIZATIONS, 1):
            print(f"  [{idx}] {name}")
        s = input("  输入编号（逗号分隔，回车=全部）: ").strip()
        if s:
            enabled = []
            for p in s.split(","):
                try:
                    n = int(p.strip()) - 1
                    if 0 <= n < len(OPTIMIZATIONS):
                        enabled.append(n)
                except ValueError:
                    pass

    if not enabled:
        info("未选择任何项目")
        pause()
        return

    print()
    cprint(SEP, "lcyan")
    info("正在执行优化...")
    print()

    for idx in enabled:
        try:
            OPTIMIZATIONS[idx][1]()
        except Exception as e:
            err(f"{OPTIMIZATIONS[idx][0]} 失败：{e}")

    print()
    cprint(SEP, "lgreen")
    cprint("  优化完成！", "lgreen")
    cprint(SEP, "lgreen")

    time.sleep(1)
    show_status()
    info("建议重启电脑使所有优化生效")
    pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
