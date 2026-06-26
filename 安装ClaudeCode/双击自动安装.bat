@echo off
title Claude Code 一键安装
setlocal enabledelayedexpansion
pushd "%~dp0"

REM 检测是否有 PowerShell
where powershell >nul 2>&1
if %errorlevel% equ 0 (
    echo 使用 PowerShell 安装（界面更友好）...
    echo ============================================
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-claude-code.ps1"
) else (
    echo 未检测到 PowerShell，使用纯 BAT 安装...
    echo ============================================
    call "%~dp0install-claude-code.bat"
)

echo.
echo ============================================
echo   安装已完成！
echo ============================================
echo.
echo   使用指南请查看: Claude-Code-使用指南.md
echo   如需清理安装文件，请运行: 清理安装文件.bat
echo.
pause
popd