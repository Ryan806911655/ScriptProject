@echo off
chcp 65001 >nul 2>&1
title 清理 Claude Code 安装文件
setlocal enabledelayedexpansion
pushd "%~dp0"

echo.
echo ============================================
echo   清理 Claude Code 安装文件
echo ============================================
echo.
echo   以下安装相关文件将被删除:
echo.
echo     * install-claude-code.ps1
echo     * install-claude-code.bat
echo     * install-claude-code.sh
echo     * install-claude-code.command
echo     * 双击安装.bat
echo     * clear.sh
echo     * clear.bat （本脚本）
echo.
echo   以下文件会保留:
echo.
echo     * Claude-Code-使用指南.md
echo     * 手动安装教程.md
echo.
echo ============================================
echo   ⚠ 删除后无法恢复！请确认已安装完成。
echo ============================================
echo.
set /p CONFIRM="   确认删除? [Y/n](直接回车=是): "
if "%CONFIRM%"=="" set CONFIRM=Y
if /i "%CONFIRM%"=="Y" (
    echo.
    echo   正在清理...

    del /f /q "%~dp0install-claude-code.ps1"     2>nul
    del /f /q "%~dp0install-claude-code.bat"     2>nul
    del /f /q "%~dp0install-claude-code.sh"      2>nul
    del /f /q "%~dp0install-claude-code.command" 2>nul
    del /f /q "%~dp0双击安装.bat"                 2>nul
    del /f /q "%~dp0clear.sh"             2>nul
    del /f /q "%~dp0clear.bat"             2>nul

    echo   [完成] 安装脚本已删除，教程文件已保留。
    echo.
    timeout /t 2 /nobreak >nul

    REM 自毁
    del /f /q "%~f0" 2>nul
) else (
    echo.
    echo   [取消] 未删除任何文件。
    echo.
    pause
)

popd
