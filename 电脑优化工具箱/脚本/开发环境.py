"""
开发环境配置 — Node.js / Python pip / Git 一键配置
"""

import os
import sys
import subprocess
import winreg
from pathlib import Path
from _utils import *


# ============================================================
# Node.js 环境配置
# ============================================================

def config_nodejs():
    """配置 Node.js 环境：迁移 npm 到 D 盘 + 国内镜像"""
    cprint("  [ Node.js ]", "lyellow")
    print()

    NODE_HOME = Path(r"C:\Program Files\nodejs")

    # 检测 node
    try:
        r = subprocess.run(["node", "-v"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            ok(f"Node.js 版本：{r.stdout.strip()}")
        else:
            warn("Node.js 似乎未正确安装")
            return
    except FileNotFoundError:
        warn("未检测到 Node.js，请先安装：https://nodejs.org/")
        return
    except Exception as e:
        warn(f"检测失败：{e}")
        return

    if not NODE_HOME.exists():
        warn("未找到 Node.js 目录，跳过环境配置")
        return

    # 选择 npm 目录
    print()
    print("  npm 全局包存放位置：")
    print("  [1] D 盘（推荐，节省 C 盘空间）")
    print("  [2] C 盘默认位置")
    print("  [3] 自定义路径")
    print()

    choice = input("  请选择（默认 1）: ").strip()

    if choice == "2":
        npm_global = Path.home() / "npm-global"
        npm_cache = Path.home() / "npm-cache"
    elif choice == "3":
        custom = input("  请输入路径（如 E:\\nodejs）: ").strip()
        if not custom:
            info("已取消")
            return
        npm_global = Path(custom) / "node_global"
        npm_cache = Path(custom) / "node_cache"
    else:
        drive = input("  目标盘符（默认 D）: ").strip() or "D"
        npm_global = Path(f"{drive}:\\nodejs\\node_global")
        npm_cache = Path(f"{drive}:\\nodejs\\node_cache")

    # 创建目录
    try:
        npm_global.mkdir(parents=True, exist_ok=True)
        npm_cache.mkdir(parents=True, exist_ok=True)
        ok(f"npm 全局目录：{npm_global}")
        ok(f"npm 缓存目录：{npm_cache}")
    except Exception as e:
        err(f"创建目录失败：{e}")
        return

    # 配置 npm
    try:
        subprocess.run(["npm", "config", "set", "prefix", str(npm_global)],
                       capture_output=True, timeout=15)
        subprocess.run(["npm", "config", "set", "cache", str(npm_cache)],
                       capture_output=True, timeout=15)
    except Exception as e:
        warn(f"npm config 失败：{e}")

    # 写入 .npmrc
    try:
        npmrc = Path.home() / ".npmrc"
        npmrc.write_text(
            f"prefix={npm_global.as_posix()}\n"
            f"cache={npm_cache.as_posix()}\n",
            encoding="utf-8"
        )
        ok(f".npmrc 已写入：{npmrc}")
    except Exception:
        pass

    # 环境变量
    try:
        def set_user_env(name, value):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment",
                                  0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)

        set_user_env("NPM_CONFIG_PREFIX", str(npm_global))
        set_user_env("NPM_CONFIG_CACHE", str(npm_cache))

        # 更新 PATH
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment",
                            0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""

            paths = [p.strip() for p in current_path.split(";") if p.strip()]
            for p in [str(NODE_HOME), str(npm_global)]:
                norm = os.path.normcase(os.path.normpath(p))
                if not any(os.path.normcase(os.path.normpath(x)) == norm for x in paths):
                    paths.append(p)

            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(paths))

        # 广播环境变更
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.byref(ctypes.c_ulong())
        )
        ok("环境变量已更新")
    except Exception as e:
        warn(f"环境变量设置失败：{e}")

    # npm 镜像
    print()
    print("  是否配置 npm 国内镜像？[Y/N]: ", end="")
    if input().strip().lower() in ("", "y", "yes"):
        try:
            subprocess.run(
                ["npm", "config", "set", "registry", "https://registry.npmmirror.com"],
                capture_output=True, timeout=15
            )
            ok("npm 镜像已设为 npmmirror.com")
        except Exception:
            pass

    print()
    ok("Node.js 环境配置完成！重新打开终端后生效。")


# ============================================================
# Python pip 镜像
# ============================================================

def config_pip_mirror():
    """配置 pip 国内镜像"""
    cprint("  [ Python pip ]", "lyellow")
    print()

    try:
        r = subprocess.run([sys.executable, "-m", "pip", "--version"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            ok(f"pip 版本：{r.stdout.strip().split()[1]}")
        else:
            warn("pip 不可用")
            return
    except Exception:
        warn("pip 不可用")
        return

    print()
    print("  常用国内镜像：")
    print("  [1] 清华 TUNA（推荐）")
    print("  [2] 阿里云")
    print("  [3] 中科大 USTC")
    print("  [4] 华为云")
    print("  [0] 跳过")
    print()

    mirrors = {
        "1": ("清华 TUNA", "https://pypi.tuna.tsinghua.edu.cn/simple"),
        "2": ("阿里云",    "https://mirrors.aliyun.com/pypi/simple/"),
        "3": ("中科大",    "https://pypi.mirrors.ustc.edu.cn/simple/"),
        "4": ("华为云",    "https://repo.huaweicloud.com/repository/pypi/simple"),
    }

    choice = input("  请选择（默认 1）: ").strip() or "1"
    if choice == "0":
        return
    if choice in mirrors:
        name, url = mirrors[choice]
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "config", "set", "global.index-url", url],
                capture_output=True, timeout=15
            )
            ok(f"pip 镜像已设为「{name}」")
        except Exception as e:
            warn(f"配置失败：{e}")


# ============================================================
# Git 配置
# ============================================================

def config_git():
    """配置 Git 用户名和邮箱"""
    cprint("  [ Git ]", "lyellow")
    print()

    # 检测 Git
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            ok(r.stdout.strip())
        else:
            warn("Git 似乎未正确安装")
            return
    except FileNotFoundError:
        warn("未检测到 Git，请先安装：https://git-scm.com/")
        return

    # 检查已有配置
    try:
        name_r = subprocess.run(["git", "config", "--global", "user.name"],
                                capture_output=True, text=True, timeout=10)
        email_r = subprocess.run(["git", "config", "--global", "user.email"],
                                 capture_output=True, text=True, timeout=10)
        if name_r.stdout.strip():
            info(f"当前用户名：{name_r.stdout.strip()}")
        if email_r.stdout.strip():
            info(f"当前邮箱：  {email_r.stdout.strip()}")
    except Exception:
        pass

    print()
    print("  是否设置/修改 Git 用户信息？[Y/N]: ", end="")
    if input().strip().lower() not in ("y", "yes"):
        return

    print()
    name = input("  请输入用户名（GitHub 用户名）: ").strip()
    email = input("  请输入邮箱（GitHub 注册邮箱）: ").strip()

    if name:
        try:
            subprocess.run(["git", "config", "--global", "user.name", name],
                           capture_output=True, timeout=10)
            ok(f"用户名 -> {name}")
        except Exception as e:
            err(f"失败：{e}")

    if email:
        try:
            subprocess.run(["git", "config", "--global", "user.email", email],
                           capture_output=True, timeout=10)
            ok(f"邮箱 -> {email}")
        except Exception as e:
            err(f"失败：{e}")

    # 额外配置
    print()
    print("  是否配置常用 Git 设置？[Y/N]: ", end="")
    if input().strip().lower() in ("y", "yes"):
        git_settings = {
            "core.autocrlf": "input",           # 换行符（Windows 友好）
            "init.defaultBranch": "main",       # 默认分支
            "pull.rebase": "false",             # pull 策略
            "core.longpaths": "true",           # 长路径支持
        }
        for key, val in git_settings.items():
            subprocess.run(["git", "config", "--global", key, val],
                           capture_output=True, timeout=10)
        ok("已完成（autocrlf/默认main分支/长路径）")


# ============================================================
# 环境变量查看/编辑
# ============================================================

def show_env_vars():
    """查看关键环境变量"""
    cprint("  [ 环境变量 ]", "lyellow")
    print()

    key_vars = [
        "Path", "JAVA_HOME", "NODEJS_HOME", "NPM_CONFIG_PREFIX",
        "PYTHON_HOME", "ANDROID_HOME", "MAVEN_HOME", "GRADLE_HOME",
        "GOPATH", "GOROOT", "RUST_HOME", "CARGO_HOME",
    ]

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment",
                            0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if name in key_vars or "HOME" in name or "PATH" in name.upper():
                        display = value if len(value) < 80 else value[:77] + "..."
                        print(f"  {name} = {display}")
                    i += 1
                except OSError:
                    break
    except Exception:
        pass

    # 也检查系统级环境变量
    print()
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                            0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if name in key_vars or "HOME" in name:
                        display = value if len(value) < 80 else value[:77] + "..."
                        print(f"  [系统] {name} = {display}")
                    i += 1
                except OSError:
                    break
    except Exception:
        pass


# ============================================================
# 主菜单
# ============================================================

def main():
    cprint(SEP, "lcyan")
    cprint("       编程开发环境配置", "lwhite")
    cprint(SEP, "lcyan")
    print()

    while True:
        print("  [1] Node.js 环境配置（npm 迁移 + 镜像 + 环境变量）")
        print("  [2] Python pip 镜像配置")
        print("  [3] Git 用户信息 & 常用设置")
        print("  [4] 查看关键环境变量")
        print("  [0] 返回上级")
        print()
        choice = input("  请选择: ").strip()

        if choice == "0":
            return
        elif choice == "1":
            print()
            config_nodejs()
            print()
            pause()
        elif choice == "2":
            print()
            config_pip_mirror()
            print()
            pause()
        elif choice == "3":
            print()
            config_git()
            print()
            pause()
        elif choice == "4":
            print()
            show_env_vars()
            print()
            pause()
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
