@echo off
title Claude Code 一键安装
cd /d "%~dp0"

REM 检测 PowerShell
where powershell >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   使用 PowerShell 安装（界面更友好）...
    echo ============================================
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-claude-code.ps1"
    goto :done
)

REM 降级到 BAT 安装
echo.
echo ============================================
echo   未检测到 PowerShell，使用 BAT 安装...
echo ============================================
echo.
call "%~dp0install-claude-code.bat"

:done
echo.
echo ============================================
echo   安装完成！
echo ============================================
echo.
echo   使用指南: 使用指南.md
echo   安装教程: 安装教程.md
echo.
pause
