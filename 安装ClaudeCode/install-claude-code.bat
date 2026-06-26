@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM 分隔符（统一管理）
set "SEP1==============================================="
set "SEP2-----------------------------------------------"

title Claude Code 一键安装

echo.
echo !SEP1!
echo    Claude Code 一键安装脚本
echo    Node.js + Git + VS Code + Claude Code
echo !SEP1!
echo.
echo    本脚本将自动安装:
echo      1. Node.js - JavaScript 运行环境
echo      2. Git     - 版本管理工具
echo      3. VS Code - 代码编辑器
echo      4. Claude Code - AI 编程助手
echo.
echo    已安装的组件会自动跳过。
echo.

echo !SEP1!
echo  [环境检测]
echo !SEP1!

net session >nul 2>&1
if !errorlevel! neq 0 (
    echo   [X] 当前不是管理员权限运行
    echo.
    set /p ADMIN_CHOICE="   自动提升为管理员? [Y/N](推荐Y): "
    if /i "!ADMIN_CHOICE!"=="" set ADMIN_CHOICE=Y
    if /i "!ADMIN_CHOICE!"=="Y" (
        echo   正在请求管理员权限,请在UAC弹窗中点"是"...
        powershell -Command "Start-Process cmd -ArgumentList '/k cd /d \"%~dp0\" && \"%~f0\"' -Verb RunAs"
        exit /b 0
    )
    echo   将以普通权限继续。
    echo.
) else (
    echo   [OK] 管理员权限: 已获取
)

set "ARCH=x64"
if "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ARCH=arm64"
echo   [OK] 系统架构: !ARCH!

echo   正在检测网络...
set "HAS_NET=0"
ping -n 1 -w 2000 8.8.8.8 >nul 2>&1 && set "HAS_NET=1"
if "!HAS_NET!"=="0" ping -n 1 -w 2000 114.114.114.114 >nul 2>&1 && set "HAS_NET=1"
if "!HAS_NET!"=="0" ping -n 1 -w 2000 www.baidu.com >nul 2>&1 && set "HAS_NET=1"
if "!HAS_NET!"=="0" (
    echo   [失败] 网络不可用。
    pause
    exit /b 1
)
echo   [OK] 网络: 正常

set "HAS_D_DRIVE=0"
if exist "D:\" set "HAS_D_DRIVE=1"

echo.
echo !SEP1!
echo  [开始安装] - 共4个组件
echo !SEP1!

REM ============================================================
REM 1. Node.js
REM ============================================================
echo.
echo !SEP2!
echo  [1/4] Node.js - JavaScript运行环境
echo !SEP2!

REM 获取最新 LTS 版本
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "$l='v22.19.0';try{$r=Invoke-RestMethod 'https://nodejs.org/dist/index.json' -TimeoutSec 8;$x=$r|?{$_.lts}|Select -First 1;if($x.version){$l=$x.version}}catch{};$l"') do set "NODE_LATEST=%%i"
echo   最新 LTS: !NODE_LATEST!

where node >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('node -v') do set "INSTALLED_NODE=%%i"
    echo   已安装:   !INSTALLED_NODE!

    REM PowerShell 比较版本
    powershell -NoProfile -Command "$i='!INSTALLED_NODE!' -replace '^v','';$l='!NODE_LATEST!' -replace '^v','';if($i-and[Version]$i-lt[Version]$l){exit 1}else{exit 0}"
    if !errorlevel! equ 1 (
        echo   ⚠ 版本过旧 ^(!INSTALLED_NODE! -^> !NODE_LATEST!^)，可能影响 Claude Code 运行。
        echo.
        echo   [1] 更新到 !NODE_LATEST!（推荐）
        echo   [2] 跳过，保留当前版本
        echo.
        set /p NODE_CHOICE="   请选择（默认1）: "
        if "!NODE_CHOICE!"=="" set NODE_CHOICE=1
        if "!NODE_CHOICE!"=="2" (
            echo   [OK] 已跳过更新，保留 !INSTALLED_NODE!
            goto :step_npm_config
        )
        echo   将更新 Node.js 到 !NODE_LATEST!...
        goto :do_node_install
    ) else (
        echo   [OK] 已是最新 LTS 版本
        goto :step_npm_config
    )
)

echo   未检测到Node.js，将安装 !NODE_LATEST!...

:do_node_install
echo   正在安装/更新 Node.js...

where winget >nul 2>&1
if !errorlevel! equ 0 (
    echo   方式1: winget...
    winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements --silent
    if !errorlevel! equ 0 (
        call :refresh_path
        where node >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%i in ('node -v') do echo   [OK] Node.js %%i 安装成功
            goto :step_npm_config
        )
    )
    echo   winget失败,改用下载安装...
)

set "NODE_VER_NUM=!NODE_LATEST:v=!"
set "NODE_URL=https://nodejs.org/dist/!NODE_LATEST!/node-!NODE_VER_NUM!-!ARCH!.msi"
set "NODE_MIRROR=https://npmmirror.com/mirrors/node/!NODE_LATEST!/node-!NODE_VER_NUM!-!ARCH!.msi"
set "NODE_INSTALLER=%TEMP%\nodejs-installer.msi"

echo   正在下载Node.js !NODE_LATEST!...
powershell -Command "try { Invoke-WebRequest -Uri '%NODE_URL%' -OutFile '%NODE_INSTALLER%' -ErrorAction Stop } catch { exit 1 }"
if !errorlevel! neq 0 (
    echo   官方下载失败,尝试国内镜像...
    powershell -Command "try { Invoke-WebRequest -Uri '!NODE_MIRROR!' -OutFile '%NODE_INSTALLER%' -ErrorAction Stop } catch { exit 1 }"
)

if exist "%NODE_INSTALLER%" (
    echo   正在安装(静默模式)...
    msiexec /i "%NODE_INSTALLER%" /quiet /norestart
    del "%NODE_INSTALLER%" 2>nul
    call :refresh_path
    where node >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('node -v') do echo   [OK] Node.js %%i 安装成功
    ) else (
        echo   [失败] Node.js安装失败。
        echo   请手动安装: https://nodejs.org/zh-cn/download/
        pause
        exit /b 1
    )
) else (
    echo   [失败] 下载失败。
    echo   请手动安装: https://nodejs.org/zh-cn/download/
    pause
    exit /b 1
)

:step_npm_config
echo.

REM ============================================================
REM 配置 npm（镜像源 + 全局路径）
REM ============================================================
echo !SEP2!
echo   配置 npm
echo !SEP2!

set "NPM_CMD="
where npm >nul 2>&1 && set "NPM_CMD=npm"
if "!NPM_CMD!"=="" (
    if exist "C:\Program Files\nodejs\npm.cmd" set "NPM_CMD=C:\Program Files\nodejs\npm.cmd"
)
if "!NPM_CMD!"=="" (
    if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
)
if "!NPM_CMD!"=="" (
    if exist "D:\nodejs\node_global\npm.cmd" set "NPM_CMD=D:\nodejs\node_global\npm.cmd"
)
if "!NPM_CMD!"=="" (
    echo   [失败] 找不到npm。
    echo   请重新安装Node.js: https://nodejs.org/zh-cn/download/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('call "!NPM_CMD!" -v') do echo   npm版本: %%i

for /f "tokens=*" %%i in ('call "!NPM_CMD!" config get prefix') do set "NPM_PREFIX=%%i"
echo   npm全局路径: !NPM_PREFIX!

set "ON_C_DRIVE=0"
echo !NPM_PREFIX! | findstr /b /i "C:" >nul 2>&1 && set "ON_C_DRIVE=1"

if "!ON_C_DRIVE!"=="1" if "!HAS_D_DRIVE!"=="1" (
    echo.
    echo   npm全局包存放在C盘,建议迁移到D盘节省空间。
    echo.
    set /p DO_MIGRATE="   迁移到D:\nodejs\? [Y/N](推荐Y): "
    if /i "!DO_MIGRATE!"=="" set DO_MIGRATE=Y
    if /i "!DO_MIGRATE!"=="Y" (
        set "NEW_PREFIX=D:\nodejs\node_global"
        set "NEW_CACHE=D:\nodejs\node_cache"
        if not exist "!NEW_PREFIX!" mkdir "!NEW_PREFIX!" 2>nul
        if not exist "!NEW_CACHE!"  mkdir "!NEW_CACHE!"  2>nul
        call "!NPM_CMD!" config set prefix "!NEW_PREFIX!"
        call "!NPM_CMD!" config set cache  "!NEW_CACHE!"
        set "PATH=!PATH!;!NEW_PREFIX!"
        set "NPM_PREFIX=!NEW_PREFIX!"
        for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "OLD_UP=%%b"
        set "NEW_UP=!OLD_UP!;!NEW_PREFIX!"
        set "NEW_UP=!NEW_UP:;;=;!"
        setx PATH "!NEW_UP!" >nul 2>&1
        echo   [OK] 已迁移到D:\nodejs\
    )
)

echo.
echo   检查npm镜像源...
set "CURRENT_REGISTRY="
for /f "tokens=*" %%i in ('call "!NPM_CMD!" config get registry 2^>nul') do set "CURRENT_REGISTRY=%%i"
echo !CURRENT_REGISTRY! | findstr /i "npmmirror" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] 当前已使用 npmmirror.com 镜像，无需切换
) else (
    echo   当前镜像: !CURRENT_REGISTRY!
    echo   是否使用国内npm镜像加速?
    echo   中国大陆用户推荐选Y。
    set /p MIRROR_CHOICE="   使用npmmirror.com? [Y/N](推荐Y): "
    if /i "!MIRROR_CHOICE!"=="" set MIRROR_CHOICE=Y
    if /i "!MIRROR_CHOICE!"=="Y" (
        call "!NPM_CMD!" config set registry https://registry.npmmirror.com
        echo   [OK] 镜像已设置: npmmirror.com
    ) else (
        echo   [OK] 使用npm官方源
    )
)

goto :step_git

:step_git
echo.

REM ============================================================
REM 2. Git
REM ============================================================
echo !SEP2!
echo  [2/4] Git - 版本管理工具
echo !SEP2!

where git >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('git --version') do echo   已安装: %%i
    goto :step_vscode
)

echo   未检测到Git,正在安装...

where winget >nul 2>&1
if !errorlevel! equ 0 (
    echo   方式1: winget...
    winget install Git.Git --accept-package-agreements --accept-source-agreements --silent
    if !errorlevel! equ 0 (
        call :refresh_path
        where git >nul 2>&1
        if !errorlevel! equ 0 (
            for /f "tokens=*" %%i in ('git --version') do echo   [OK] %%i 安装成功
            goto :step_vscode
        )
    )
    echo   winget失败,改用下载安装...
)

set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe"
set "GIT_INSTALLER=%TEMP%\git-installer.exe"

echo   正在下载Git...
powershell -Command "try { Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%GIT_INSTALLER%' -ErrorAction Stop } catch { exit 1 }"

if exist "%GIT_INSTALLER%" (
    echo   正在安装(静默模式)...
    "%GIT_INSTALLER%" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS
    del "%GIT_INSTALLER%" 2>nul
    call :refresh_path
    where git >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('git --version') do echo   [OK] %%i 安装成功
    ) else (
        echo   [X] Git安装可能未生效,已跳过。
    )
) else (
    echo   [X] Git下载失败,已跳过。
)

:step_vscode
echo.

REM ============================================================
REM 3. VS Code
REM ============================================================
echo !SEP2!
echo  [3/4] VS Code - 代码编辑器
echo !SEP2!

REM 获取最新版本
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "try{$r=Invoke-RestMethod 'https://update.code.visualstudio.com/api/update/win32-x64/stable/latest' -TimeoutSec 8;if($r.name){$r.name}}catch{}"') do set "VSCODE_LATEST=%%i"
if defined VSCODE_LATEST echo   最新稳定版: !VSCODE_LATEST!

where code >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=1" %%i in ('code --version 2^>^&1') do set "INSTALLED_VSCODE=%%i"
    echo   已安装:   !INSTALLED_VSCODE!

    if defined VSCODE_LATEST (
        powershell -NoProfile -Command "if([Version]'!INSTALLED_VSCODE!' -lt [Version]'!VSCODE_LATEST!'){exit 1}else{exit 0}"
        if !errorlevel! equ 1 (
            echo   ⚠ 版本过旧 ^(!INSTALLED_VSCODE! -^> !VSCODE_LATEST!^)，可能影响 Claude Code 扩展运行。
            echo.
            echo   [1] 更新到 !VSCODE_LATEST!（推荐）
            echo   [2] 跳过，保留当前版本
            echo.
            set /p VS_CHOICE="   请选择（默认1）: "
            if "!VS_CHOICE!"=="" set VS_CHOICE=1
            if "!VS_CHOICE!"=="2" (
                echo   [OK] 已跳过更新，保留 !INSTALLED_VSCODE!
                goto :step_npm
            )
            goto :do_vscode_install
        ) else (
            echo   [OK] 已是最新版本
        )
    )
    goto :step_npm
)

if exist "C:\Program Files\Microsoft VS Code\bin\code.cmd" (
    echo   已安装(默认路径)
    goto :step_npm
)
if exist "%LocalAppData%\Programs\Microsoft VS Code\bin\code.cmd" (
    echo   已安装(用户路径)
    goto :step_npm
)

echo   未检测到VS Code，正在安装...

:do_vscode_install
echo   正在安装/更新 VS Code...

where winget >nul 2>&1
if !errorlevel! equ 0 (
    echo   方式1: winget...
    winget install Microsoft.VisualStudioCode --accept-package-agreements --accept-source-agreements --silent
    if !errorlevel! equ 0 (
        call :refresh_path
        echo   [OK] VS Code安装成功
        goto :step_npm
    )
    echo   winget失败,改用下载安装...
)

set "VSCODE_URL=https://update.code.visualstudio.com/latest/win32-!ARCH!-user/stable"
set "VSCODE_INSTALLER=%TEMP%\vscode-installer.exe"

echo   正在下载VS Code...
powershell -Command "try { Invoke-WebRequest -Uri '%VSCODE_URL%' -OutFile '%VSCODE_INSTALLER%' -ErrorAction Stop } catch { exit 1 }"

if exist "%VSCODE_INSTALLER%" (
    echo   正在安装(静默模式)...
    "%VSCODE_INSTALLER%" /VERYSILENT /MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,addtopath
    del "%VSCODE_INSTALLER%" 2>nul
    call :refresh_path
    echo   [OK] VS Code安装成功
) else (
    echo   [X] VS Code下载失败,已跳过。
)

:step_npm
echo.

REM ============================================================
REM 4. Claude Code
REM ============================================================
echo !SEP2!
echo  [4/4] Claude Code - AI编程助手
echo !SEP2!

REM 验证 npm 可用（安装 Node.js 后已配置）
if "!NPM_CMD!"=="" (
    echo   [失败] 找不到npm。
    echo   请重新安装Node.js: https://nodejs.org/zh-cn/download/
    pause
    exit /b 1
)

REM ============================================================
REM 检测 Claude Code 是否已安装 + 版本对比
REM ============================================================

REM 获取 npm 上的最新版本
for /f "tokens=*" %%i in ('call "!NPM_CMD!" view @anthropic-ai/claude-code version 2^>nul') do set "CC_LATEST=%%i"
if defined CC_LATEST echo   npm 最新版: !CC_LATEST!

set "CC_SKIP=0"
where claude >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('claude --version 2^>^&1') do set "EXISTING_CC=%%i"
    echo.
    echo   [检测] Claude Code 已安装: !EXISTING_CC!

    if defined CC_LATEST (
        if not "!EXISTING_CC!"=="!CC_LATEST!" (
            echo   ⚠ 当前版本 ^(!EXISTING_CC!^) 低于最新版 ^(!CC_LATEST!^)
        )
    )
    echo.
    echo   [1] 更新到最新版（推荐）
    echo   [2] 重装（覆盖安装）
    echo   [3] 跳过安装
    echo.
    set /p CC_CHOICE="   请选择（默认1）: "
    if "!CC_CHOICE!"=="" set CC_CHOICE=1
    if "!CC_CHOICE!"=="3" (
        echo   [OK] 已跳过 Claude Code 安装
        set "CC_SKIP=1"
    )
    if "!CC_CHOICE!"=="2" (
        echo   将覆盖安装...
    )
    if "!CC_CHOICE!"=="1" (
        echo   将更新到最新版...
    )
)

if "!CC_SKIP!"=="0" (
    echo.
    echo   正在安装Claude Code(约1-3分钟)...
    call "!NPM_CMD!" install -g @anthropic-ai/claude-code

    if !errorlevel! neq 0 (
        echo.
        echo   [失败] Claude Code安装失败。
        echo.
        echo   请手动尝试:
        echo     npm config set registry https://registry.npmmirror.com
        echo     npm install -g @anthropic-ai/claude-code
        echo.
        pause
        exit /b 1
    )

    echo   [OK] Claude Code安装完成
)

set "CC_VER="
where claude >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('claude --version 2^>^&1') do set "CC_VER=%%i"
)

echo.
echo !SEP1!
echo  [安装完成!]
echo !SEP1!
if defined CC_VER echo   Claude Code版本: !CC_VER!
echo !SEP1!

echo.
echo !SEP1!
echo  [API配置] - Claude Code需要API密钥
echo !SEP1!
echo.
echo   请选择API提供商:
echo.
echo   [1] DeepSeek      (国内推荐,便宜)
echo   [2] Anthropic      (官方OAuth登录)
echo   [3] Anthropic      (官方API Key)
echo   [4] 其他第三方      (自定义地址)
echo   [0] 跳过配置
echo.
set /p PROVIDER_CHOICE="   请输入数字(默认1): "
if "!PROVIDER_CHOICE!"=="" set PROVIDER_CHOICE=1

if "!PROVIDER_CHOICE!"=="0" goto :done
if "!PROVIDER_CHOICE!"=="2" (
    echo.
    echo   打开新终端,输入claude,浏览器会弹出OAuth登录。
    goto :done
)

echo.
if "!PROVIDER_CHOICE!"=="1" (
    echo   获取API Key: https://platform.deepseek.com
    echo.
    set /p API_KEY="   请粘贴DeepSeek API Key: "
    if "!API_KEY!"=="" echo   [跳过] 未输入Key。 & goto :done
    setx ANTHROPIC_BASE_URL "https://api.deepseek.com/anthropic" >nul
    setx ANTHROPIC_AUTH_TOKEN "!API_KEY!" >nul
    echo   [OK] DeepSeek API Key和端点已保存
    echo.
    set /p SET_MODELS="   是否配置模型映射? [Y/N](推荐Y): "
    if /i "!SET_MODELS!"=="" set SET_MODELS=Y
    if /i "!SET_MODELS!"=="Y" (
        setx ANTHROPIC_DEFAULT_SONNET_MODEL "deepseek-v4-pro" >nul
        setx ANTHROPIC_DEFAULT_OPUS_MODEL "deepseek-v4-pro" >nul
        setx ANTHROPIC_DEFAULT_HAIKU_MODEL "deepseek-v4-flash" >nul
        echo   [OK] 模型映射已配置
    )
) else if "!PROVIDER_CHOICE!"=="3" (
    echo   获取API Key: https://console.anthropic.com/settings/keys
    echo.
    set /p API_KEY="   请粘贴Anthropic API Key: "
    if "!API_KEY!"=="" echo   [跳过] 未输入Key。 & goto :done
    setx ANTHROPIC_API_KEY "!API_KEY!" >nul
    echo   [OK] Anthropic API Key已保存
) else (
    echo   第三方需支持Anthropic兼容API端点。
    set /p CUSTOM_KEY="   请输入API Key: "
    if "!CUSTOM_KEY!"=="" echo   [跳过] 未输入Key。 & goto :done
    setx ANTHROPIC_AUTH_TOKEN "!CUSTOM_KEY!" >nul
    set /p CUSTOM_URL="   API端点地址: "
    if not "!CUSTOM_URL!"=="" setx ANTHROPIC_BASE_URL "!CUSTOM_URL!" >nul
    set /p CUSTOM_MODEL="   默认模型名称: "
    if not "!CUSTOM_MODEL!"=="" (
        setx ANTHROPIC_DEFAULT_SONNET_MODEL "!CUSTOM_MODEL!" >nul
        setx ANTHROPIC_DEFAULT_OPUS_MODEL "!CUSTOM_MODEL!" >nul
    )
    echo   [OK] 第三方已配置
)

:done
echo.
echo !SEP1!
echo  [大功告成!]
echo !SEP1!
echo.
echo   打开新终端,输入 claude 开始使用!
echo.
echo   常用命令:
echo     claude             启动交互模式
echo     claude "问题"       直接提问
echo     claude --help       查看帮助
echo     claude --update     更新到最新版
echo     code .              在当前目录打开VS Code
echo.
echo   VS Code用户: 扩展市场搜索 Claude Code
echo.
echo !SEP1!
echo   安装已完成！
echo !SEP1!
echo.
echo   使用指南请查看: Claude-Code-使用指南.md
echo   如需清理安装文件，请运行: 清理安装文件.bat
echo !SEP1!
pause
exit /b 0

REM ============================================================
REM 辅助:刷新PATH
REM ============================================================
:refresh_path
for /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "MACHINE_PATH=%%b"
for /f "skip=2 tokens=3*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%b"
set "COMBINED_PATH="
if defined MACHINE_PATH set "COMBINED_PATH=!MACHINE_PATH!"
if defined USER_PATH (
    if defined COMBINED_PATH (set "COMBINED_PATH=!COMBINED_PATH!;!USER_PATH!") else (set "COMBINED_PATH=!USER_PATH!")
)
if defined COMBINED_PATH (
    endlocal & set "PATH=%COMBINED_PATH%"
    setlocal enabledelayedexpansion
)
goto :eof