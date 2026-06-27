<#
.SYNOPSIS
    电脑优化工具箱 V2.0 启动器
.DESCRIPTION
    右键 → "使用 PowerShell 运行"
    首次使用需执行：Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#>

$Host.UI.RawUI.WindowTitle = "电脑优化工具箱 V2.0"
Set-Location $PSScriptRoot

# ============================================
# 检测 Python，未安装则提示安装
# ============================================
function Find-Python {
    foreach ($c in @("python", "python3", "py")) {
        $found = Get-Command $c -ErrorAction SilentlyContinue
        if ($found) { return $c }
    }
    return $null
}

function Install-Python {
    Write-Host ""
    Write-Host "  ============================================" -ForegroundColor Cyan
    Write-Host "  未检测到 Python，部分功能需要 Python 才能运行" -ForegroundColor Yellow
    Write-Host "  ============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  是否自动安装 Python？" -ForegroundColor White
    Write-Host "  [Y] 是 — 通过 winget 自动安装（推荐）" -ForegroundColor Green
    Write-Host "  [N] 否 — 退出" -ForegroundColor Red
    Write-Host ""

    $choice = Read-Host "  请选择（Y/N）"
    if ($choice -notin @("Y", "y", "yes")) {
        Write-Host ""
        Write-Host "  已取消。您也可以手动安装：" -ForegroundColor Yellow
        Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host "  安装时请勾选 'Add Python to PATH'" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "按回车退出"
        exit 1
    }

    Write-Host ""
    Write-Host "  正在检测 winget..." -ForegroundColor Cyan

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "  正在通过 winget 安装 Python 3.13..." -ForegroundColor Cyan
        Write-Host "  （可能需要几分钟，请耐心等待）" -ForegroundColor Gray
        Write-Host ""

        winget install Python.Python.3.13 --accept-package-agreements --accept-source-agreements

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "  Python 安装完成！" -ForegroundColor Green

            # 刷新 PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

            $py = Find-Python
            if ($py) {
                Write-Host "  检测到 Python: $py" -ForegroundColor Green
                Write-Host ""
                Read-Host "按回车继续启动工具箱"
                return $py
            }

            Write-Host "  安装完成但未在 PATH 中找到 Python，请重启后重试" -ForegroundColor Yellow
            Read-Host "按回车退出"
            exit 1
        } else {
            Write-Host "  winget 安装失败，正在打开下载页面..." -ForegroundColor Yellow
            Start-Process "https://www.python.org/downloads/"
            Write-Host "  请手动下载安装，勾选 'Add Python to PATH'" -ForegroundColor Yellow
            Read-Host "按回车退出"
            exit 1
        }
    } else {
        Write-Host "  winget 不可用，正在打开下载页面..." -ForegroundColor Yellow
        Start-Process "https://www.python.org/downloads/"
        Write-Host "  请手动下载安装，勾选 'Add Python to PATH'" -ForegroundColor Yellow
        Read-Host "按回车退出"
        exit 1
    }
}

$PythonCmd = Find-Python
if (-not $PythonCmd) {
    $PythonCmd = Install-Python
    if (-not $PythonCmd) { exit 1 }
}

# ============================================
# 自动提权
# ============================================
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $psi.WorkingDirectory = $PSScriptRoot
    $psi.Verb = "RunAs"
    $psi.UseShellExecute = $true
    [System.Diagnostics.Process]::Start($psi) | Out-Null
    exit 0
}

# ============================================
# 启动主程序
# ============================================
$Script = Join-Path $PSScriptRoot "脚本\工具箱.py"
& $PythonCmd $Script
if ($LASTEXITCODE -ne 0) { Read-Host "按回车退出" }
