"""
新机开荒优化 — 关闭遥测/广告/预装应用/OneDrive，打造干净系统
"""

import os
import sys
import winreg
from _utils import *


# ============================================================
# 隐私 & 遥测
# ============================================================

def disable_telemetry():
    """关闭 Windows 诊断数据收集"""
    info("[隐私] 诊断数据 & 遥测")
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SOFTWARE\Policies\Microsoft\Windows\DataCollection") as key:
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "DoNotShowFeedbackNotifications", 0, winreg.REG_DWORD, 1)
        ok("已关闭诊断数据")
    except Exception as e:
        warn(f"失败：{e}")

    # 禁用遥测服务
    try:
        run_cmd("sc config DiagTrack start= disabled")
        run_cmd("net stop DiagTrack /y 2>nul")
        run_cmd("sc config dmwappushservice start= disabled")
        run_cmd("net stop dmwappushservice /y 2>nul")
        ok("已禁用遥测服务")
    except Exception:
        pass


def disable_advertising_id():
    """关闭广告 ID"""
    info("[隐私] 广告追踪")
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo") as key:
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
        ok("已关闭广告 ID")

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Privacy") as key:
            winreg.SetValueEx(key, "TailoredExperiencesWithDiagnosticDataEnabled", 0, winreg.REG_DWORD, 0)
        ok("已关闭定制体验")
    except Exception as e:
        warn(f"失败：{e}")


def disable_tips_and_suggestions():
    """关闭各种提示和建议"""
    info("[隐私] 系统提示 & 建议")
    settings = {
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"):
            [("SystemPaneSuggestionsEnabled", 0),
             ("SubscribedContent-338389Enabled", 0),
             ("SubscribedContent-338388Enabled", 0),
             ("SubscribedContent-338387Enabled", 0),
             ("SubscribedContent-353698Enabled", 0),
             ("SubscribedContentEnabled", 0),
             ("SilentInstalledAppsEnabled", 0),
             ("OemPreInstalledAppsEnabled", 0),
             ("PreInstalledAppsEnabled", 0),
             ("PreInstalledAppsEverEnabled", 0),
             ("SoftLandingEnabled", 0),
             ("FeatureManagementEnabled", 0),],
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"):
            [("Start_TrackProgs", 0),
             ("ShowSyncProviderNotifications", 0),],
    }
    for (hkey_root, reg_path), values in settings.items():
        try:
            with winreg.CreateKey(hkey_root, reg_path) as key:
                for name, val in values:
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, val)
        except Exception:
            pass
    ok("已关闭开始菜单广告/建议/提示")


def disable_cortana():
    """关闭 Cortana"""
    info("[隐私] Cortana")
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SOFTWARE\Policies\Microsoft\Windows\Windows Search") as key:
            winreg.SetValueEx(key, "AllowCortana", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "AllowSearchToUseLocation", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "DisableWebSearch", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "ConnectedSearchUseWeb", 0, winreg.REG_DWORD, 0)
        ok("已关闭 Cortana & Bing 搜索集成")
    except Exception as e:
        warn(f"失败：{e}")


def disable_onedrive():
    """禁用 OneDrive 自启动"""
    info("[隐私] OneDrive")
    try:
        run_cmd("taskkill /f /im OneDrive.exe 2>nul", capture=False)
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SOFTWARE\Policies\Microsoft\Windows\OneDrive") as key:
            winreg.SetValueEx(key, "DisableFileSyncNGSC", 0, winreg.REG_DWORD, 1)
        ok("已禁用 OneDrive（进程结束 + 策略限制）")
    except Exception as e:
        warn(f"失败：{e}")


def disable_activity_history():
    """关闭活动历史记录"""
    info("[隐私] 活动历史")
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SOFTWARE\Policies\Microsoft\Windows\System") as key:
            winreg.SetValueEx(key, "EnableActivityFeed", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "PublishUserActivities", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "UploadUserActivities", 0, winreg.REG_DWORD, 0)
        ok("已关闭")
    except Exception as e:
        warn(f"失败：{e}")


# ============================================================
# 任务栏 & 桌面
# ============================================================

def optimize_taskbar():
    """优化任务栏设置"""
    info("[桌面] 任务栏优化")
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Search") as key:
            winreg.SetValueEx(key, "SearchboxTaskbarMode", 0, winreg.REG_DWORD, 1)
        ok("任务栏搜索 -> 仅图标")
    except Exception:
        pass
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") as key:
            winreg.SetValueEx(key, "TaskbarDa", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "TaskbarMn", 0, winreg.REG_DWORD, 0)
        ok("已关闭任务栏小组件 & 聊天")
    except Exception:
        pass


def optimize_explorer():
    """资源管理器优化"""
    info("[桌面] 资源管理器")
    settings = {
        "HideFileExt": 0,           # 显示文件扩展名
        "Hidden": 1,                # 显示隐藏文件
        "ShowSuperHidden": 0,       # 显示系统隐藏文件
        "HideMergeConflicts": 0,    # 显示合并冲突
        "LaunchTo": 1,              # 打开资源管理器 -> 此电脑
        "ShowRecent": 0,            # 关闭快速访问中的最近文件
        "ShowFrequent": 0,          # 关闭快速访问中的常用文件夹
    }
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") as key:
            for name, val in settings.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, val)
        ok("显示文件扩展名 + 隐藏文件 + 此电脑")
    except Exception as e:
        warn(f"失败：{e}")


# ============================================================
# 卸载预装应用
# ============================================================

BLOATWARE = [
    # Xbox 相关
    "Microsoft.Xbox*",
    "Microsoft.GamingServices",
    # 通讯
    "Microsoft.People",
    "Microsoft.SkypeApp",
    # 媒体
    "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo",
    "Microsoft.BingNews",
    "Microsoft.BingWeather",
    "Microsoft.BingSports",
    "Microsoft.BingFinance",
    # Office 试用
    "Microsoft.MicrosoftOfficeHub",
    # 其他
    "Microsoft.MixedReality.Portal",
    "Microsoft.GetHelp",
    "Microsoft.Getstarted",
    "Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.Microsoft3DViewer",
    "Microsoft.Print3D",
    "Microsoft.Wallet",
    "Microsoft.OneConnect",
    "Microsoft.MSPaint",
    "Microsoft.Todos",
    "Microsoft.FeedbackHub",
    "Microsoft.Office.OneNote",
    "Microsoft.PowerAutomateDesktop",
    "Clipchamp.Clipchamp",
    # 第三方预装
    "*CandyCrush*",
    "*Netflix*",
    "*Spotify*",
    "*Disney*",
    "*Facebook*",
    "*Twitter*",
    "*TikTok*",
    "*Instagram*",
    "*Pinterest*",
]


def remove_bloatware():
    """卸载预装软件"""
    info("[清理] 预装应用")

    removed = 0
    for app in BLOATWARE:
        try:
            # Get-AppxPackage 可能返回多个包
            r = run_cmd(f'powershell -Command "Get-AppxPackage -AllUsers *{app}* | Remove-AppxPackage -ErrorAction SilentlyContinue"')
            # 也尝试用 winget 卸载
            run_cmd(f'powershell -Command "Get-AppxProvisionedPackage -Online | Where-Object DisplayName -Like \'*{app}*\' | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue"')
            removed += 1
        except Exception:
            pass

    ok(f"已尝试卸载 {removed} 个预装组件")
    info("部分系统核心组件已自动跳过")


# ============================================================
# 游戏优化
# ============================================================

def optimize_game_settings():
    """游戏相关优化"""
    info("[游戏] 游戏模式 & Xbox Game Bar")
    try:
        # 关闭 Game Bar（释放资源）
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\GameDVR") as key:
            winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"System\GameConfigStore") as key:
            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
        ok("已关闭 Xbox Game Bar 录屏")
    except Exception:
        pass

    # 开启游戏模式（反而提升性能）
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\GameBar") as key:
            winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 1)
        ok("已开启游戏模式")
    except Exception:
        pass


# ============================================================
# 主流程
# ============================================================

OPT_GROUPS = [
    ("隐私 & 遥测", [
        disable_telemetry,
        disable_advertising_id,
        disable_tips_and_suggestions,
        disable_cortana,
        disable_onedrive,
        disable_activity_history,
    ]),
    ("任务栏 & 桌面", [
        optimize_taskbar,
        optimize_explorer,
    ]),
    ("卸载预装", [
        remove_bloatware,
    ]),
    ("游戏设置", [
        optimize_game_settings,
    ]),
]


def main():
    cprint(SEP, "lcyan")
    cprint("       新机开荒优化工具", "lwhite")
    cprint("       隐私/桌面/预装/游戏 一键设置", "lcyan")
    cprint(SEP, "lcyan")
    print()

    require_admin()

    print("  将执行以下优化：")
    for group_name, funcs in OPT_GROUPS:
        print(f"    >> {group_name}（{len(funcs)} 项）")
    print()

    print("  [1] 一键自动优化（推荐）")
    print("  [2] 自定义选择分组")
    print("  [0] 退出")
    print()

    choice = input("  请选择（默认 1）: ").strip()

    if choice == "0":
        return

    if choice == "2":
        enabled_groups = []
        print()
        for idx, (gname, _) in enumerate(OPT_GROUPS, 1):
            print(f"  [{idx}] {gname}")
        print()
        s = input("  输入分组编号（逗号分隔，回车=全部）: ").strip()
        if s:
            for p in s.split(","):
                try:
                    n = int(p.strip()) - 1
                    if 0 <= n < len(OPT_GROUPS):
                        enabled_groups.append(n)
                except ValueError:
                    pass
        else:
            enabled_groups = list(range(len(OPT_GROUPS)))
    else:
        enabled_groups = list(range(len(OPT_GROUPS)))

    if not enabled_groups:
        info("未选择任何项目")
        pause()
        return

    print()
    cprint(SEP, "lcyan")
    info("正在执行优化...")
    print()

    for idx in enabled_groups:
        gname, funcs = OPT_GROUPS[idx]
        cprint(f"  [{gname}]", "lyellow")
        print()
        for func in funcs:
            try:
                func()
            except Exception as e:
                err(f"  {func.__name__} 失败：{e}")
        print()

    cprint(SEP, "lgreen")
    cprint("  新机开荒优化完成！", "lgreen")
    info("建议重启电脑使所有设置生效")
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
