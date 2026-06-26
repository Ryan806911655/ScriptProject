#Requires -Version 5.1
$host.UI.RawUI.WindowTitle = "Claude Code 一键安装"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 分隔符（统一管理，方便调整宽度）
$SEP1 = "=" * 48    # 一级分隔（大段标题、环境检测、完成）
$SEP2 = "-" * 48    # 二级分隔（组件安装步骤）

Write-Host ""
Write-Host $SEP1
Write-Host "   Claude Code 一键安装脚本"
Write-Host "   Node.js + Git + VS Code + Claude Code"
Write-Host $SEP1
Write-Host ""
Write-Host "   本脚本将自动安装:"
Write-Host "    1. Node.js（JavaScript 运行环境）"
Write-Host "    2. Git（版本管理工具）"
Write-Host "    3. VS Code（代码编辑器）"
Write-Host "    4. Claude Code 并配置 API 密钥"
Write-Host ""
Write-Host "   已安装的组件会自动跳过，不会重复安装。"
Write-Host ""

Write-Host $SEP1
Write-Host " [环境检测]"
Write-Host $SEP1

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "   ⚠ 当前不是管理员权限运行" -ForegroundColor Yellow
    Write-Host ""
    $choice = Read-Host "   是否提升为管理员? [Y/N]（推荐 Y）"
    if ($choice -eq "" -or $choice -eq "Y" -or $choice -eq "y") {
        Write-Host "   正在提权，请在弹出的 UAC 窗口点 [是]..."
        Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        exit 0
    }
    Write-Host "   将以普通权限继续（部分安装可能失败）。" -ForegroundColor Yellow
    Write-Host ""
}
else {
    Write-Host "   [OK] 管理员权限: 已获取" -ForegroundColor Green
}

$arch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "arm64" } else { "x64" }
Write-Host "   [OK] 系统架构: $arch" -ForegroundColor Green

Write-Host "   正在检测网络..."
$hasNet = $false
if (Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet) { $hasNet = $true }
elseif (Test-Connection -ComputerName 114.114.114.114 -Count 1 -Quiet) { $hasNet = $true }
elseif (Test-Connection -ComputerName www.baidu.com -Count 1 -Quiet) { $hasNet = $true }

if (-not $hasNet) {
    Write-Host "   [失败] 网络不可用，无法继续安装。" -ForegroundColor Red
    Read-Host "   按回车退出"
    exit 1
}
Write-Host "   [OK] 网络: 正常" -ForegroundColor Green

$hasDDrive = Test-Path "D:\"

Write-Host ""
Write-Host $SEP1
Write-Host " [开始安装] - 共 4 个组件"
Write-Host $SEP1

# ============================================================
# 1. Node.js
# ============================================================
Write-Host ""
Write-Host $SEP2
Write-Host " [1/4] Node.js - JavaScript 运行环境"
Write-Host $SEP2

# 获取最新 LTS 版本
$nodeLatest = "v22.19.0"
try {
    $r = Invoke-RestMethod -Uri "https://nodejs.org/dist/index.json" -TimeoutSec 10
    $lts = $r | Where-Object { $_.lts -ne $false } | Select-Object -First 1
    if ($lts) { $nodeLatest = $lts.version }
}
catch {}
Write-Host "   最新 LTS: $nodeLatest"

$nodeInstalled = $false
$doNodeInstall = $false
try {
    $nodeVer = & node -v 2>$null
    if ($LASTEXITCODE -eq 0) {
        $installedVer = $nodeVer -replace "^v", ""
        $latestVer   = $nodeLatest -replace "^v", ""
        Write-Host "   已安装:   $nodeVer"

        if ([Version]$installedVer -lt [Version]$latestVer) {
            Write-Host "   ⚠ 版本过旧 ($nodeVer → $nodeLatest)，可能影响 Claude Code 运行。" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "   [1] 更新到 $nodeLatest（推荐）"
            Write-Host "   [2] 跳过，保留当前版本"
            Write-Host ""
            $nodeChoice = Read-Host "   请选择（默认 1）"
            if ($nodeChoice -eq "2") {
                Write-Host "   [OK] 已跳过更新，保留 $nodeVer" -ForegroundColor Green
                $nodeInstalled = $true
            }
            else {
                $doNodeInstall = $true
            }
        }
        else {
            Write-Host "   [OK] 已是最新 LTS 版本" -ForegroundColor Green
            $nodeInstalled = $true
        }
    }
}
catch {}

if (-not $nodeInstalled -and -not $doNodeInstall) {
    Write-Host "   未检测到 Node.js，将安装 $nodeLatest..."
    $doNodeInstall = $true
}

if ($doNodeInstall) {
    Write-Host "   正在安装/更新 Node.js..."

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "   方式1: winget..."
        winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements --silent
        if ($LASTEXITCODE -eq 0) {
            Refresh-Path
            try { $v = & node -v; Write-Host "   [OK] Node.js $v 安装成功" -ForegroundColor Green; $nodeInstalled = $true }
            catch {}
        }
    }

    if (-not $nodeInstalled) {
        if ($winget) { Write-Host "   winget 失败，改用下载安装..." }

        $nodeVerNum = $nodeLatest -replace "^v", ""
        $nodeUrl = "https://nodejs.org/dist/$nodeLatest/node-$nodeVerNum-$arch.msi"
        $nodeMirror = "https://npmmirror.com/mirrors/node/$nodeLatest/node-$nodeVerNum-$arch.msi"
        $installer = "$env:TEMP\nodejs-installer.msi"

        Write-Host "   正在下载 Node.js $nodeLatest..."
        try { Invoke-WebRequest -Uri $nodeUrl -OutFile $installer -ErrorAction Stop }
        catch {
            Write-Host "   官方下载失败，尝试国内镜像..."
            try { Invoke-WebRequest -Uri $nodeMirror -OutFile $installer -ErrorAction Stop }
            catch {
                Write-Host "   [失败] 下载失败。" -ForegroundColor Red
                Write-Host "   请手动安装: https://nodejs.org/zh-cn/download/"
                Read-Host "   按回车退出"
                exit 1
            }
        }

        Write-Host "   正在安装（静默模式）..."
        Start-Process msiexec.exe -ArgumentList "/i `"$installer`" /quiet /norestart" -Wait
        Remove-Item $installer -Force -ErrorAction SilentlyContinue
        Refresh-Path

        try {
            $v = & node -v
            Write-Host "   [OK] Node.js $v 安装成功" -ForegroundColor Green
            $nodeInstalled = $true
        }
        catch {
            Write-Host "   [失败] Node.js 安装失败。" -ForegroundColor Red
            Write-Host "   请手动安装: https://nodejs.org/zh-cn/download/"
            Read-Host "   按回车退出"
            exit 1
        }
    }
}

# ============================================================
# 配置 npm（镜像源 + 全局路径）
# ============================================================
Write-Host ""
Write-Host $SEP2
Write-Host "   配置 npm"
Write-Host $SEP2

# 查找 npm
$npmCmd = $null
$npmPaths = @(
    "npm",
    "C:\Program Files\nodejs\npm.cmd",
    "$env:ProgramFiles\nodejs\npm.cmd",
    "D:\nodejs\node_global\npm.cmd"
)
foreach ($p in $npmPaths) {
    try {
        $testCmd = if ($p -eq "npm") { "npm" } else { $p }
        & $testCmd -v 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $npmCmd = $testCmd
            break
        }
    }
    catch {}
}

if (-not $npmCmd) {
    Write-Host "   [失败] 找不到 npm，Node.js 可能安装不完整。" -ForegroundColor Red
    Write-Host "   请重新安装 Node.js: https://nodejs.org/zh-cn/download/"
    Read-Host "   按回车退出"
    exit 1
}

$npmVer = & $npmCmd -v 2>$null
Write-Host "   npm 版本: $npmVer"

$npmPrefix = try { (& $npmCmd config get prefix) } catch { "$env:APPDATA\npm" }
Write-Host "   npm 全局路径: $npmPrefix"

if ($npmPrefix -match "^C:" -and $hasDDrive) {
    Write-Host ""
    Write-Host "   npm 全局包存放在 C 盘，建议迁移到 D 盘以节省空间。" -ForegroundColor Yellow
    Write-Host ""
    $choice = Read-Host "   是否迁移到 D:\nodejs\? [Y/N]（推荐 Y）"
    if ($choice -eq "" -or $choice -eq "Y" -or $choice -eq "y") {
        $newPrefix = "D:\nodejs\node_global"
        $newCache = "D:\nodejs\node_cache"
        New-Item -ItemType Directory -Path $newPrefix -Force | Out-Null
        New-Item -ItemType Directory -Path $newCache -Force | Out-Null
        & $npmCmd config set prefix $newPrefix
        & $npmCmd config set cache $newCache
        $env:Path = "$env:Path;$newPrefix"
        $npmPrefix = $newPrefix
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($userPath -notlike "*$newPrefix*") {
            [Environment]::SetEnvironmentVariable("Path", "$userPath;$newPrefix", "User")
        }
        Write-Host "   [OK] 已迁移到 $newPrefix" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "   检查 npm 镜像源..."
$currentRegistry = try { & $npmCmd config get registry 2>$null } catch { "" }
if ($currentRegistry -match "npmmirror") {
    Write-Host "   [OK] 当前已使用 npmmirror.com 镜像，无需切换" -ForegroundColor Green
}
else {
    Write-Host "   当前镜像: $currentRegistry" -ForegroundColor Yellow
    Write-Host "   是否使用国内 npm 镜像加速下载?"
    Write-Host "   中国大陆用户推荐选 Y。" -ForegroundColor Yellow
    $choice = Read-Host "   使用 npmmirror.com? [Y/N]（推荐 Y）"
    if ($choice -eq "" -or $choice -eq "Y" -or $choice -eq "y") {
        & $npmCmd config set registry https://registry.npmmirror.com
        Write-Host "   [OK] 镜像已设置: npmmirror.com" -ForegroundColor Green
    }
    else {
        Write-Host "   [OK] 使用 npm 官方源" -ForegroundColor Green
    }
}

# ============================================================
# 2. Git
# ============================================================
Write-Host ""
Write-Host $SEP2
Write-Host " [2/4] Git - 版本管理工具"
Write-Host $SEP2

$gitInstalled = $false
try {
    $gitVer = & git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   已安装: $gitVer" -ForegroundColor Green
        $gitInstalled = $true
    }
}
catch {}

if (-not $gitInstalled) {
    Write-Host "   未检测到 Git，正在安装..."

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "   方式1: winget..."
        winget install Git.Git --accept-package-agreements --accept-source-agreements --silent
        if ($LASTEXITCODE -eq 0) {
            Refresh-Path
            try { $v = & git --version; Write-Host "   [OK] $v 安装成功" -ForegroundColor Green; $gitInstalled = $true }
            catch {}
        }
    }

    if (-not $gitInstalled) {
        if ($winget) { Write-Host "   winget 失败，改用下载安装..." }

        $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe"
        $installer = "$env:TEMP\git-installer.exe"

        Write-Host "   正在下载 Git..."
        try { Invoke-WebRequest -Uri $gitUrl -OutFile $installer -ErrorAction Stop }
        catch { Write-Host "   [注意] Git 下载失败，已跳过。" -ForegroundColor Yellow }

        if (Test-Path $installer) {
            Write-Host "   正在安装（静默模式）..."
            Start-Process $installer -ArgumentList "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS" -Wait
            Remove-Item $installer -Force -ErrorAction SilentlyContinue
            Refresh-Path
            try {
                $v = & git --version
                Write-Host "   [OK] $v 安装成功" -ForegroundColor Green
                $gitInstalled = $true
            }
            catch { Write-Host "   [注意] Git 安装可能未生效，已跳过。" -ForegroundColor Yellow }
        }
    }
}

# ============================================================
# 3. VS Code
# ============================================================
Write-Host ""
Write-Host $SEP2
Write-Host " [3/4] VS Code - 代码编辑器"
Write-Host $SEP2

# 获取 VS Code 最新版本
$vscodeLatest = ""
try {
    $vsUpdateApi = Invoke-RestMethod "https://update.code.visualstudio.com/api/update/win32-$arch/stable/latest" -TimeoutSec 8
    if ($vsUpdateApi.name) { $vscodeLatest = $vsUpdateApi.name }
}
catch {}
if ($vscodeLatest) { Write-Host "   最新稳定版: $vscodeLatest" }

$vscodeInstalled = $false
$doVscodeUpdate = $false
try {
    $codeVer = & code --version 2>$null | Select-Object -First 1
    if ($codeVer) {
        Write-Host "   已安装:   $codeVer"

        if ($vscodeLatest -and [Version]$codeVer -lt [Version]$vscodeLatest) {
            Write-Host "   ⚠ 版本过旧 ($codeVer → $vscodeLatest)，可能影响 Claude Code 扩展运行。" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "   [1] 更新到 $vscodeLatest（推荐）"
            Write-Host "   [2] 跳过，保留当前版本"
            Write-Host ""
            $vsChoice = Read-Host "   请选择（默认 1）"
            if ($vsChoice -eq "2") {
                Write-Host "   [OK] 已跳过更新，保留 $codeVer" -ForegroundColor Green
                $vscodeInstalled = $true
            }
            else {
                $doVscodeUpdate = $true
            }
        }
        else {
            Write-Host "   [OK] 已是最新版本" -ForegroundColor Green
            $vscodeInstalled = $true
        }
    }
}
catch {}

if (-not $vscodeInstalled -and -not $doVscodeUpdate) {
    if (Test-Path "C:\Program Files\Microsoft VS Code\bin\code.cmd") {
        Write-Host "   已安装（默认路径）" -ForegroundColor Green
        $vscodeInstalled = $true
    }
    elseif (Test-Path "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd") {
        Write-Host "   已安装（用户路径）" -ForegroundColor Green
        $vscodeInstalled = $true
    }
}

if (-not $vscodeInstalled -or $doVscodeUpdate) {
    Write-Host "   正在安装/更新 VS Code..."

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "   方式1: winget..."
        winget install Microsoft.VisualStudioCode --accept-package-agreements --accept-source-agreements --silent
        if ($LASTEXITCODE -eq 0) {
            Refresh-Path
            Write-Host "   [OK] VS Code 安装成功" -ForegroundColor Green
            $vscodeInstalled = $true
        }
    }

    if (-not $vscodeInstalled) {
        if ($winget) { Write-Host "   winget 失败，改用下载安装..." }

        $vscodeUrl = "https://update.code.visualstudio.com/latest/win32-$arch-user/stable"
        $installer = "$env:TEMP\vscode-installer.exe"

        Write-Host "   正在下载 VS Code..."
        try { Invoke-WebRequest -Uri $vscodeUrl -OutFile $installer -ErrorAction Stop }
        catch { Write-Host "   [注意] VS Code 下载失败，已跳过。" -ForegroundColor Yellow }

        if (Test-Path $installer) {
            Write-Host "   正在安装（静默模式）..."
            Start-Process $installer -ArgumentList "/VERYSILENT /MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,addtopath" -Wait
            Remove-Item $installer -Force -ErrorAction SilentlyContinue
            Refresh-Path
            Write-Host "   [OK] VS Code 安装成功" -ForegroundColor Green
            $vscodeInstalled = $true
        }
    }
}

# ============================================================
# 4. Claude Code
# ============================================================
Write-Host ""
Write-Host $SEP2
Write-Host " [4/4] Claude Code - AI 编程助手"
Write-Host $SEP2

# 验证 npm 可用（安装 Node.js 后已配置）
if (-not $npmCmd) {
    Write-Host "   [失败] 找不到 npm，Node.js 可能安装不完整。" -ForegroundColor Red
    Write-Host "   请重新安装 Node.js: https://nodejs.org/zh-cn/download/"
    Read-Host "   按回车退出"
    exit 1
}

# ============================================================
# 检测 Claude Code 是否已安装 + 版本对比
# ============================================================

# 获取 npm 上的最新版本
$ccLatest = ""
try {
    $ccLatest = & $npmCmd view @anthropic-ai/claude-code version 2>$null
    if ($ccLatest) { Write-Host "   npm 最新版: $ccLatest" }
}
catch {}

$claudeAlreadyInstalled = $false
try {
    $existingCC = & claude --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "   [检测] Claude Code 已安装: $existingCC"

        if ($ccLatest -and $existingCC -ne $ccLatest) {
            Write-Host "   ⚠ 当前版本 ($existingCC) 低于最新版 ($ccLatest)" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "   [1] 更新到最新版（推荐）"
        Write-Host "   [2] 重装（覆盖安装）"
        Write-Host "   [3] 跳过安装"
        Write-Host ""
        $ccChoice = Read-Host "   请选择（默认 1）"
        if ($ccChoice -eq "3") {
            Write-Host "   [OK] 已跳过 Claude Code 安装" -ForegroundColor Green
            $claudeAlreadyInstalled = $true
        }
        elseif ($ccChoice -eq "2") {
            Write-Host "   将覆盖安装..." -ForegroundColor Yellow
        }
        else {
            Write-Host "   将更新到最新版..." -ForegroundColor Cyan
        }
    }
}
catch {}

if (-not $claudeAlreadyInstalled) {
    Write-Host ""
    Write-Host "   正在安装 Claude Code（约 1-3 分钟）..." -ForegroundColor Cyan
    & $npmCmd install -g @anthropic-ai/claude-code

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "   [失败] Claude Code 安装失败。" -ForegroundColor Red
        Write-Host ""
        Write-Host "   请手动尝试:"
        Write-Host "     npm config set registry https://registry.npmmirror.com"
        Write-Host "     npm install -g @anthropic-ai/claude-code"
        Write-Host ""
        Read-Host "   按回车退出"
        exit 1
    }

    Write-Host "   [OK] Claude Code 安装完成" -ForegroundColor Green
}

try { $ccVer = & claude --version 2>$null } catch {}

Write-Host ""
Write-Host $SEP1
Write-Host " [安装完成!]"
Write-Host $SEP1
if ($ccVer) { Write-Host "   Claude Code 版本: $ccVer" }

# ============================================================
# API 配置
# ============================================================
Write-Host ""
Write-Host $SEP1
Write-Host " [API 配置]"
Write-Host " Claude Code 需要一个 API 密钥来驱动 AI"
Write-Host $SEP1
Write-Host ""
Write-Host "   请选择 API 提供商:"
Write-Host ""
Write-Host "   [1] DeepSeek      (国内推荐, 便宜)"
Write-Host "   [2] Anthropic      (官方 OAuth 登录)"
Write-Host "   [3] Anthropic      (官方 API Key)"
Write-Host "   [4] 其他第三方      (自定义地址)"
Write-Host "   [0] 跳过配置"
Write-Host ""
$choice = Read-Host "   请输入数字（默认 1）"
if ($choice -eq "" -or $choice -eq "1") { $choice = "1" }

if ($choice -eq "0") {
    # skip
}
elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "   打开新终端，输入 claude，浏览器会弹出 OAuth 登录页面。"
}
elseif ($choice -eq "1") {
    Write-Host ""
    Write-Host "   获取 API Key: https://platform.deepseek.com"
    Write-Host ""
    $apiKey = Read-Host "   请粘贴你的 DeepSeek API Key"
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "   [跳过] 未输入 Key。" -ForegroundColor Yellow
    }
    else {
        [Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic", "User")
        [Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", $apiKey, "User")
        Write-Host "   [OK] DeepSeek API Key 和端点已保存" -ForegroundColor Green
        Write-Host ""
        $setModels = Read-Host "   是否配置模型映射? [Y/N]（推荐 Y）"
        if ($setModels -eq "" -or $setModels -eq "Y" -or $setModels -eq "y") {
            [Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_SONNET_MODEL", "deepseek-v4-pro", "User")
            [Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_OPUS_MODEL", "deepseek-v4-pro", "User")
            [Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_HAIKU_MODEL", "deepseek-v4-flash", "User")
            Write-Host "   [OK] 模型映射已配置" -ForegroundColor Green
        }
    }
}
elseif ($choice -eq "3") {
    Write-Host ""
    Write-Host "   获取 API Key: https://console.anthropic.com/settings/keys"
    Write-Host ""
    $apiKey = Read-Host "   请粘贴你的 Anthropic API Key"
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "   [跳过] 未输入 Key。" -ForegroundColor Yellow
    }
    else {
        [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $apiKey, "User")
        Write-Host "   [OK] Anthropic API Key 已保存" -ForegroundColor Green
    }
}
elseif ($choice -eq "4") {
    Write-Host ""
    Write-Host "   第三方需要支持 Anthropic 兼容 API 端点。"
    $apiKey = Read-Host "   请输入 API Key"
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "   [跳过] 未输入 Key。" -ForegroundColor Yellow
    }
    else {
        [Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", $apiKey, "User")
        $customUrl = Read-Host "   API 端点地址（如 https://api.openrouter.ai/api）"
        if ($customUrl) { [Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $customUrl, "User") }
        $customModel = Read-Host "   默认模型名称"
        if ($customModel) {
            [Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_SONNET_MODEL", $customModel, "User")
            [Environment]::SetEnvironmentVariable("ANTHROPIC_DEFAULT_OPUS_MODEL", $customModel, "User")
        }
        Write-Host "   [OK] 第三方提供商已配置" -ForegroundColor Green
    }
}
else {
    Write-Host "   [跳过] 无效选择。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host $SEP1
Write-Host " [大功告成!]"
Write-Host $SEP1
Write-Host ""
Write-Host "   打开新的终端，输入 claude 开始使用!"
Write-Host ""
Write-Host "   常用命令:"
Write-Host "     claude             启动交互模式"
Write-Host "     claude `"问题`"       直接提问"
Write-Host "     claude --help       查看帮助"
Write-Host "     claude --update     更新到最新版"
Write-Host "     code .              在当前目录打开 VS Code"
Write-Host ""
Write-Host "   VS Code 用户:"
Write-Host "     在扩展市场搜索 Claude Code 安装官方扩展"
Write-Host ""
Write-Host $SEP1
Read-Host "   按回车退出"

function Refresh-Path {
    $m = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $u = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = ($m, $u -join ";")
}