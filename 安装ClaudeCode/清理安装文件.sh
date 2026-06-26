#!/bin/bash
# ============================================================
#  清理 Claude Code 安装文件
#  安装完成后运行此脚本即可删除所有安装工具
# ============================================================

echo ""
echo "============================================"
echo "   清理 Claude Code 安装文件"
echo "============================================"
echo ""
echo "   以下安装相关文件将被删除:"
echo ""
echo "     * install-claude-code.ps1"
echo "     * install-claude-code.bat"
echo "     * install-claude-code.sh"
echo "     * install-claude-code.command"
echo "     * 双击安装.bat"
echo "     * 清理安装文件.bat"
echo "     * 清理安装文件.sh （本脚本）"
echo ""
echo "   以下文件会保留:"
echo ""
echo "     * Claude-Code-使用指南.md"
echo "     * 手动安装教程.md"
echo "     * 远程安装命令.md"
echo ""
echo "============================================"
echo "   ⚠ 删除后无法恢复！请确认已安装完成。"
echo "============================================"
echo ""
read -p "   确认删除? [Y/n](直接回车=是): " confirm
confirm=${confirm:-Y}

if [ "$confirm" = "Y" ] || [ "$confirm" = "y" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

    echo ""
    echo "   正在清理..."

    rm -f "$SCRIPT_DIR/install-claude-code.ps1"     2>/dev/null
    rm -f "$SCRIPT_DIR/install-claude-code.bat"     2>/dev/null
    rm -f "$SCRIPT_DIR/install-claude-code.sh"      2>/dev/null
    rm -f "$SCRIPT_DIR/install-claude-code.command" 2>/dev/null
    rm -f "$SCRIPT_DIR/双击安装.bat"                 2>/dev/null
    rm -f "$SCRIPT_DIR/清理安装文件.bat"             2>/dev/null

    echo "   [完成] 安装脚本已删除，教程文件已保留。"
    echo ""
    sleep 2

    # 自毁
    rm -f "$0" 2>/dev/null
else
    echo ""
    echo "   [取消] 未删除任何文件。"
    echo ""
fi
