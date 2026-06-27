@echo off
title 清理 Claude Code 安装文件
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================
echo   清理 Claude Code 安装文件
echo ============================================
echo.
echo   将删除以下安装脚本:
echo     - install-claude-code.ps1
echo     - install-claude-code.bat
echo     - install-claude-code.sh
echo     - install-claude-code.command
echo     - 双击安装.bat
echo     - clear.sh
echo     - clear.bat（本脚本）
echo.
echo   保留文件:
echo     - 使用指南.md
echo     - 安装教程.md
echo.
echo   删除后无法恢复！请确认已安装完成。
echo ============================================
echo.
set /p CONFIRM="   确认删除? [Y/N]（直接回车=是）: "
if "%CONFIRM%"=="" set CONFIRM=Y
if /i not "%CONFIRM%"=="Y" (
    echo.
    echo   [取消] 未删除任何文件。
    echo.
    pause
    exit /b 0
)

echo.
echo   正在清理...

for %%f in (
    "install-claude-code.ps1"
    "install-claude-code.bat"
    "install-claude-code.sh"
    "install-claude-code.command"
    "双击安装.bat"
    "clear.sh"
) do (
    if exist "%~dp0%%~f" (
        del /f /q "%~dp0%%~f" 2>nul
        echo     [OK] %%~f
    )
)

echo.
echo   [完成] 安装脚本已删除，教程文件已保留。
timeout /t 2 /nobreak >nul

REM 自毁 — 用 cmd /c 启动子进程延迟删除，避免占用
start "" /b cmd /c "timeout /t 1 /nobreak >nul & del /f /q "%~f0" 2>nul"
exit /b 0
